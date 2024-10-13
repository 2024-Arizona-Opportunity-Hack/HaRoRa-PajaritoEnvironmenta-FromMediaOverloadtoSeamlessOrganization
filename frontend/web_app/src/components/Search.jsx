import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { searchMedia } from '../api/api';
import TagEditor from './TagEditor';

function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryFromUrl = searchParams.get('q') || ''; // Get the 'q' param from the URL
  const [query, setQuery] = useState(queryFromUrl); // Set initial state from the URL query
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedUuid, setSelectedUuid] = useState(null);

  // Function to handle search and update URL
  const handleSearch = () => {
    // Update the URL with the query parameter
    setSearchParams({ q: query });
  };

  // Fetch search results when component mounts or URL query changes
  useEffect(() => {
    const fetchSearchResults = async () => {
      if (queryFromUrl) {
        setLoading(true);
        try {
          const data = await searchMedia(queryFromUrl);
          console.log(data)
          setResults(data['results']);
        } catch (error) {
          alert('Error fetching search results.');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchSearchResults(); // Fetch results on mount or query change
    console.log(queryFromUrl)
  }, [queryFromUrl]); // Dependency is the query parameter in the URL

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
        <div className="mt-4 grid grid-cols-3 gap-4">
          {results.slice(0, 9).map((item) => (
            <div key={item.id} className="card bg-base-100 shadow-md">
              <figure>
                <img
                  src={item.thumbnailUrl}
                  alt={item.url}
                  className="w-full h-48 object-cover"
                />
              </figure>
              <div className="card-body">
                <h2 className="card-title text-sm">{item.title}</h2>
                <p className="text-xs text-gray-600">
                  Tags: {item.tags}
                </p>
                <div className="card-actions justify-end">
                  <button
                    className="btn btn-xs btn-outline"
                    onClick={() => setSelectedUuid(item.uuid)}
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
