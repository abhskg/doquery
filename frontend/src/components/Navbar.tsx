import React from 'react';
import Link from 'next/link';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-primary-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold">
          RAG Query
        </Link>
        <div className="flex space-x-4">
          <Link href="/" className="hover:text-primary-200">
            Home
          </Link>
          <Link href="/about" className="hover:text-primary-200">
            About
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 