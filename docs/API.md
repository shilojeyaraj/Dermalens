# API Reference

The backend is a FastAPI service (`apps/api`). When running locally it serves
interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Base URL:

- Local: `http://localhost:8000`
- Production: routed via the frontend as `/api/*` (Vercel rewrite → Cloud Run)

Most non-public endpoints expect a Supabase JWT:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Health & metrics

| Method | Path               | Description                          |
| ------ | ------------------ | ------------------------------------ |
| GET    | `/health`          | Liveness/readiness check             |
| GET    | `/metrics`         | Performance metrics                  |
| GET    | `/metrics/summary` | Aggregated metrics summary           |
| GET    | `/cache/stats`     | Cache statistics                     |
| POST   | `/cache/clear`     | Clear server-side caches             |

### Authentication

| Method | Path            | Description                       |
| ------ | --------------- | --------------------------------- |
| POST   | `/auth/signup`  | Create an account                 |
| POST   | `/auth/signin`  | Sign in, returns access token     |
| POST   | `/auth/refresh` | Refresh an access token           |

### Profiles

| Method | Path            | Description                       |
| ------ | --------------- | --------------------------------- |
| GET    | `/profile`      | Get the current user's profile    |
| PUT    | `/profile`      | Update the current user's profile |
| GET    | `/skin-profile` | Get the user's skin profile       |
| POST   | `/skin-profile` | Create the user's skin profile    |
| PUT    | `/skin-profile` | Update the user's skin profile    |

### Skin analysis

| Method | Path                              | Description                                  |
| ------ | --------------------------------- | -------------------------------------------- |
| POST   | `/analyze-skin`                   | Analyze a single face image                  |
| POST   | `/analyze-skin-enhanced`          | Enhanced analysis (Vertex AI / ensemble)     |
| POST   | `/analyze-skin-multi-angle`       | Analyze multiple angles                      |
| POST   | `/analyze-comprehensive-enhanced` | Full pipeline (analysis + recs + routine)    |

### Recommendations & products

| Method | Path                               | Description                              |
| ------ | ---------------------------------- | ---------------------------------------- |
| POST   | `/recommendations-enhanced`        | Product recommendations from analysis    |
| POST   | `/generate-profile-recommendations`| Recommendations from a skin profile      |
| GET    | `/products/search`                 | Search products (query params)           |
| GET    | `/products/trending`               | Trending products                        |
| POST   | `/search-products`                 | Search products (request body)           |
| POST   | `/generate-routine`                | Generate a personalized skincare routine |

### Admin

| Method | Path                       | Description                          |
| ------ | -------------------------- | ------------------------------------ |
| POST   | `/admin/seed-elasticsearch`| Seed the Elasticsearch product index |

## Example

```bash
# Health check
curl http://localhost:8000/health

# Search products
curl "http://localhost:8000/products/search?query=vitamin%20c%20serum"

# Authenticated request
curl http://localhost:8000/profile \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

> The tables above are generated from the route definitions in
> `apps/api/main.py`. For exact request/response schemas, see the live Swagger UI
> at `/docs`, which is always in sync with the running code.
