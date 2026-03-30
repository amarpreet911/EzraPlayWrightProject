# Privacy & Security Test Scenarios

Concise reference for testing privacy/IDOR/data exposure issues in the Ezra API.

---

## Critical Findings to Validate

### 1. **Password Grant Used from Browser** [HIGH]

**Finding:** Frontend sends raw credentials via password grant directly to token endpoint.

```
POST /individuals/member/connect/token
grant_type=password
username=...
password=...
scope=offline_access
```

**Test:**
- Verify refresh tokens are not returned to browser  
- Check no MFA bypass exists  
- Confirm rate-limiting on token endpoint  

**Fix:** Move to Authorization Code + PKCE; remove password grant for SPAs.

---

### 2. **Sensitive GET Endpoints Missing Cache Headers** [HIGH]

**Finding:** Medical and member profile data returned via GET without `Cache-Control: no-store`.

**Affected endpoints:**
- `GET /individuals/api/members` (returns DOB, phone, address, email)
- `GET /diagnostics/api/medicaldata/forms/mq/submissions/{id}/data`
- `GET /diagnostics/api/medicaldata/forms/mq/submissions/{uuid}/detail`

**Inspect response headers for:**
```
Cache-Control: no-store
Pragma: no-cache
Expires: 0
```

**Why it matters:** PHI may be cached in browsers, proxies, logs, monitoring tools.

**Fix:** Add strict no-store cache directives to all sensitive GET responses.

---

### 3. **Excessive Sensitive Data Exposure** [MEDIUM]

**Finding:** API responses return more data than UI actually needs.

**Examples:**
- Member endpoint returns: name, email, phone, DOB, address, gender, timezone, internal IDs
- Medical questionnaire returns: allergies, BP, cholesterol, cancer history, diabetes, family history, medications, smoking history, renal disease, ethnicity

**Test:** Compare what UI displays vs. what API returns. Flag overexposure.

**Fix:** Apply data minimization—return only required fields per UI state.

---

### 4. **Strong IDOR / Broken Object-Level Authorization Surface** [CRITICAL]

**Affected endpoints:**
- `GET/POST /diagnostics/api/medicaldata/forms/mq/submissions/{submission_id}/data`
- `GET /diagnostics/api/medicaldata/forms/mq/submissions/{uuid}/detail`
- `GET /diagnostics/api/medicaldata/requiresAsyncIc/{uuid}`
- `POST /diagnostics/api/medicaldata/forms/mq/submissions/{id}/complete`

**Pattern:** Direct object references using both:
- Numeric IDs: `3113`
- UUIDs: `060c6829-21b4-4178-a105-50b8e4450bdd`

**Test (in authorized environment):**
1. Change submission ID from `3113` to `3112`, `3114`, etc. → Confirm 403/404
2. If UUID-based, try another encounter ID from different session → Confirm 403/404
3. Verify server **never** returns another user's data
4. Test with lower-privilege account against higher-privilege data

**Red flags:**
- Any `2xx` response with foreign data = **security violation**
- Inconsistent authorization between numeric and UUID endpoints

---

### 5. **SignalR Negotiate Returns Tokens with PII Claims** [MEDIUM]

**Affected endpoints:**
- `POST /packages/encounters/negotiate?negotiateVersion=1`
- `POST /task/api/tasknoteshub/negotiate?negotiateVersion=1`

**Finding:** Hub access tokens contain user-identifying claims:
```
sub, email, given_name, family_name, name, role, scope, environment
```

**Test:**
- Can user subscribe to hub channels not belonging to them?
- Can hub parameters be altered to expose other users' messages?
- Review JWT claims for necessity

**Fix:** 
- Minimize claims (remove email, name, etc. if not needed)
- Enforce strict channel/hub subscription authorization
- Validate hub permissions server-side

---

## Secondary Findings

### 6. Infrastructure Disclosure [LOW]
Internal hostnames exposed in negotiate responses and cookies:
- `platform-signalr-dev.service.signalr.net`
- `ezra-taskservice-stage.azurewebsites.net`

**Fix:** Reduce external-facing infrastructure details.

### 7. HSTS Short-Term [LOW]
Current: `Strict-Transport-Security: max-age=2592000` (~30 days)  
Recommendation: Extend to 1+ year on production.

---

## Testing Priority

**Do these first (highest impact):**
1. IDOR: Change `submission_id=3113` to nearby values
2. Cache headers: Inspect GET responses for sensitive endpoints
3. Password grant: Review token endpoint and refresh token handling
4. Claim minimization: Check SignalR negotiate token payload

**Then:**
5. Data minimization: Compare API payloads vs. UI needs
6. Hub authorization: Test cross-user channel access

---

## Quick Checklist

- [ ] IDOR test: numeric submission IDs
- [ ] IDOR test: UUID encounter IDs  
- [ ] Cache headers present on sensitive GET?
- [ ] Token endpoint using password grant?
- [ ] Refresh tokens returned to browser?
- [ ] SignalR negotiate token claims minimized?
- [ ] Hub subscriptions properly scoped?
- [ ] Member endpoint returns only necessary fields?
- [ ] Medical questionnaire endpoint data minimized?

---

## Most Likely Bug Location

If you can only test one endpoint first:

```
GET /diagnostics/api/medicaldata/forms/mq/submissions/3113/data
```

**Action:** Duplicate request in Burp/DevTools, change `3113` to `3112` or `3114`.  
If you get anything except clean authorization failure → **you've found the main issue.**

---

*Reference: Privacy & IDOR analysis from Burp traffic review, March 2026.*

