# Frontend — Agile User Story Generator

Next.js (App Router) UI for the Agile User Story Generator. It lets users
describe a feature or upload a voice note, then renders the generated user
story as styled markdown.

## Development

```bash
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000). The backend must be
running on port 8000 (see the root [README](../README.md)); override the API
address with `NEXT_PUBLIC_API_URL`.

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm dev
```

## Scripts

| Script        | Purpose                       |
| ------------- | ----------------------------- |
| `pnpm dev`    | Start the development server  |
| `pnpm build`  | Create a production build     |
| `pnpm start`  | Serve the production build    |
| `pnpm lint`   | Run ESLint                    |
