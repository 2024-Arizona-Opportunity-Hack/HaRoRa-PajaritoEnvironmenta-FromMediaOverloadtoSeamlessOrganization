import { useState } from 'react';
import { searchMedia } from '../api/api';
import TagEditor from './TagEditor';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedUuid, setSelectedUuid] = useState(null);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const data = await searchMedia(query);
      setResults(data);
    } catch (error) {
      alert('Error fetching search results.');
    } finally {
      setLoading(false);
    }
  };

  const closeTagEditor = () => {
    setSelectedUuid(null);
    // Optionally refresh search results after editing tags
    handleSearch();
  };

  return (
    <div className="p-4">
      {/* Search Bar */}
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

      {/* Loading Indicator */}
      {loading && (
        <div className="flex justify-center items-center mt-4">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      )}

      {/* Search Results */}
      {!loading && results.length > 0 && (
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {results.map((item) => (
            <div key={item.id} className="card bg-base-100 shadow-md">
              <figure>
                <img
                  src={item.thumbnailUrl}
                  alt={item.filename}
                  className="w-full h-48 object-cover"
                />
              </figure>
              <div className="card-body">
                <h2 className="card-title">{item.filename}</h2>
                <p className="text-sm text-gray-600">
                  Tags: {item.tags.join(', ')}
                </p>
                <div className="card-actions justify-end">
                  <button
                    className="btn btn-sm btn-outline"
                    onClick={() => setSelectedUuid(item.id)}
                  >
                    Edit Tags
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results Message */}
      {!loading && results.length === 0 && query && (
        <div className="mt-4 text-center">
          <p className="text-gray-500">No results found for "{query}".</p>
        </div>
      )}

      {/* Tag Editor Modal */}
      {selectedUuid && <TagEditor uuid={selectedUuid} onClose={closeTagEditor} />}
    </div>
  );
}

export default Search;
