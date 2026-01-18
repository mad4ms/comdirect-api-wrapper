# OpenAPI Client Generation

This project uses a **generated Python OpenAPI client** for low-level communication with the Comdirect API.
The generated client lives in:

`src/openapi_client`

It is derived from Comdirect’s official Swagger/OpenAPI specification and **must not be edited manually**.

---

## When to Regenerate

Regenerate the client **only** when one of the following applies:

1. Comdirect publishes an updated Swagger/OpenAPI specification.
2. The OpenAPI generator version changes and affects output structure or runtime behavior.
3. A schema defect is fixed or added in the **spec patch step** (see below).

---

## Requirements

The generation process requires:

- `curl` – to download the Swagger spec
- `openapi-generator-cli` – for client generation
- Python environment with **Pydantic v2**

---

## How to Regenerate

Run the provided helper script:

```bash
./scripts/bootstrap_client.sh
```

### What the Script Does

1.  **Downloads** the official Comdirect Swagger specification
    `https://kunde.comdirect.de/cms/media/comdirect_rest_api_swagger.json`

2.  **Applies a mandatory patch** to the spec to correct known schema defects
    (e.g. `CurrencyString`, `DateString` incorrectly modeled as objects instead of strings).

3.  **Generates** a Python OpenAPI client using the `python` generator (Pydantic v2).

4.  **Deletes** the previous `src/openapi_client` directory.

5.  **Installs** the freshly generated client into `src/openapi_client`.

6.  **Cleans up** all temporary artifacts.

> ⚠️ **The patch step is required.**
> Without it, runtime validation errors will occur even if generation succeeds.

---

## Important Design Notes

### Spec Patching (Non-Optional)

The Comdirect Swagger specification contains schema mismatches where primitive API responses (e.g. `"EUR"`, `"2024-01-31"`) are declared as objects.

These are fixed **before generation**, not at runtime.
Runtime monkey-patching is intentionally avoided.

### Generated Code Policy

- `src/openapi_client` is committed to the repository.
- The generated code is treated as vendor code.
- All business logic must live outside this directory.

---

## Manual Steps After Generation

After regeneration, Git will show changes in `src/openapi_client`.

Perform the following checks:

1.  **Review changes**
    ```bash
    git diff src/openapi_client
    ```

2.  **Verify schema sanity**
    Ensure no object-wrappers reappear:
    ```bash
    rg "__root__" src/openapi_client || echo "OK"
    ```

3.  **Update domain mappers if needed**
    - Location: `src/comdirect_api/domain/`
    - Only required if Comdirect adds or removes fields.

4.  **Run example client**
    ```bash
    python examples/basic_example.py
    ```

---

## What Must Never Be Done

- ❌ **Editing files inside `src/openapi_client` manually**
- ❌ **Runtime monkey-patching of generated models**
- ❌ **Regenerating without applying the spec patch**
- ❌ **Mixing Pydantic v1 and v2 generators**

---

## Summary

- OpenAPI client generation is **deterministic and reproducible**
- Schema defects are fixed **at the spec level**
- Generated code is **committed and treated as immutable**
- Pydantic v2 is the supported runtime
