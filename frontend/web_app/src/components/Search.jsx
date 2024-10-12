// components/Search.jsx
import { useState } from 'react';
import axios from 'axios';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    // Make an API call to search media
    // Replace '/search' with your actual search endpoint
    const response = await axios.get('/search', { params: { q: query } });
    setResults(response.data);
  };

  return (
    <div className="p-4">
      <div className="flex">
        <input
          type="text"
          placeholder="Search..."
          className="input input-bordered w-full"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn btn-primary ml-2" onClick={handleSearch}>
          Search
        </button>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4">
        {results.map((item) => (
          <div key={item.id} className="card shadow">
            <figure>
              <img src={item.url} alt={item.tags.join(', ')} />
            </figure>
            <div className="card-body">
              <h2 className="card-title">{item.filename}</h2>
              <p>Tags: {item.tags.join(', ')}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Search;
