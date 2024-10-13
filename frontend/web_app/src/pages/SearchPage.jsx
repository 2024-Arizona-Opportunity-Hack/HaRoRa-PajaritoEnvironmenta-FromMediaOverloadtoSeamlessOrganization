// src/pages/SearchPage.jsx
import React from 'react';
import Search from '../components/Search';

function SearchPage() {
  return (
    <div className="container mx-auto max-w-4xl">
      <h1 className="text-2xl font-bold my-4">Search Media</h1>
      <Search />
    </div>
  );
}

export default SearchPage;
