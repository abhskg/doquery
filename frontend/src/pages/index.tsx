import Head from 'next/head';
import { Inter } from 'next/font/google';
import Layout from '@/components/Layout';
import UploadForm from '@/components/UploadForm';
import QueryForm from '@/components/QueryForm';

const inter = Inter({ subsets: ['latin'] });

export default function Home() {
  return (
    <>
      <Head>
        <title>RAG Query App</title>
        <meta name="description" content="Query your documents using AI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-8 text-center">RAG Query Application</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
              <UploadForm />
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">Query Documents</h2>
              <QueryForm />
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
} 