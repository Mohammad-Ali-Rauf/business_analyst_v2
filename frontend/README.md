# Frontend — Agile User Story Generator

Next.js (App Router) UI for the Agile User Story Generator. It lets users
describe a feature or upload a voice note, then renders the generated user
story as styled markdown.

## Development

```bash
yarn install
yarn dev
```

Open [http://localhost:3000](http://localhost:3000). The backend must be
running on port 8000 (see the root [README](../README.md)); override the API
address with `NEXT_PUBLIC_API_URL`.

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 yarn dev
```

## Scripts

| Script        | Purpose                       |
| ------------- | ----------------------------- |
| `yarn dev`    | Start the development server  |
| `yarn build`  | Create a production build     |
| `yarn start`  | Serve the production build    |
| `yarn lint`   | Run ESLint                    |
