# RAG Query Frontend

This is the frontend for the RAG Query application, which allows users to upload documents and query them using natural language.

## Features

- Upload documents (PDF, DOCX, TXT)
- Query documents using natural language
- View AI-generated answers

## Technologies

- Next.js
- React
- TypeScript
- Tailwind CSS
- Axios for API requests

## Getting Started

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Run the development server:
```bash
npm run dev
# or
yarn dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Building for Production

```bash
npm run build
# or
yarn build
```

Then, you can start the production server:

```bash
npm run start
# or
yarn start
```

## API Integration

The frontend is configured to proxy API requests to the backend server running at `http://localhost:8000`. This is set up in the `next.config.js` file. 