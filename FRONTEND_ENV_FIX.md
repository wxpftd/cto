# Frontend DNS Resolution Fix

## Problem

When running the frontend locally (outside Docker), it was trying to connect to `http://api:8000` which resulted in the error:

```
net::ERR_NAME_NOT_RESOLVED
```

This happened because the hostname `api` is a Docker service name that only works inside the Docker network, not from the host machine's browser.

## Root Cause

The `docker-compose.yml` file sets `VITE_API_URL=http://api:8000` for the frontend service, which is correct when running inside Docker. However, when developers run the frontend locally using `npm run dev` or `make frontend-dev`, the browser cannot resolve the `api` hostname.

## Solution

Created a `frontend/.env` file with the correct localhost URL for local development:

```
VITE_API_URL=http://localhost:8000
```

### How It Works

- **Local Development**: When running `npm run dev` outside Docker, Vite reads the `.env` file and uses `http://localhost:8000`
- **Docker Development**: When running `docker-compose up`, the environment variable in `docker-compose.yml` overrides the `.env` file, setting it to `http://api:8000`

This approach provides the best of both worlds - correct configuration for both Docker and local development.

## Changes Made

1. **Created `frontend/.env`**: Contains `VITE_API_URL=http://localhost:8000` for local development
2. **Updated `frontend/.gitignore`**: Added `.env` to prevent committing environment-specific configuration
3. **Updated `frontend/README.md`**: Added troubleshooting section explaining this issue and the Docker vs local development setup
4. **Updated `README.md`**: Added note in the Frontend Quick Start section about creating the `.env` file

## Testing

After these changes, developers should:

1. Stop any running frontend dev server
2. Restart the frontend: `npm run dev` or `make frontend-dev`
3. Open http://localhost:5173
4. Verify API calls go to `http://localhost:8000` instead of `http://api:8000`

## Notes

- The `.env.example` file already existed with the correct configuration
- The `frontend/src/api/client.ts` already had a fallback to `http://localhost:8000`, but environment variables take precedence
- This fix ensures consistent behavior across different development environments
