// src/components/Search.jsx

import { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { searchMedia } from '../api/api.jsx';
import TagEditor from './TagEditor';

function Search() {
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();
    const queryFromUrl = searchParams.get('q') || '';
    const pageFromUrl = parseInt(searchParams.get('page')) || 1;

    const [query, setQuery] = useState(queryFromUrl);
    const [results, setResults] = useState([]);
    const [filteredResults, setFilteredResults] = useState([]);
    const [availableTags, setAvailableTags] = useState([]);
    const [selectedTags, setSelectedTags] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedUuid, setSelectedUuid] = useState(null);
    const [currentPage, setCurrentPage] = useState(pageFromUrl);
    const [totalPages, setTotalPages] = useState(1);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);
    const pageSize = 10;

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    // Handle search and update URL
    const handleSearch = () => {
        setCurrentPage(1);
        setSearchParams({ q: query, page: 1 });
    };

    // Fetch search results
    useEffect(() => {
        const fetchSearchResults = async () => {
            if (queryFromUrl) {
                setLoading(true);
                try {
                    const data = await searchMedia(queryFromUrl, currentPage, pageSize);
                    setResults(data.results || []);
                    setTotalPages(data.total_pages || 1);

                    // Extract unique tags from results
                    const tagsSet = new Set();
                    data.results.forEach((item) => {
                        item.tags.forEach((tag) => tagsSet.add(tag));
                    });
                    setAvailableTags(Array.from(tagsSet));
                } catch (error) {
                    if (error.response && error.response.status === 404) {
                        alert('No results found.');
                    } else {
                        alert('Error fetching search results.');
                    }
                    setResults([]);
                    setAvailableTags([]);
                    setTotalPages(1);
                } finally {
                    setLoading(false);
                }
            } else {
                setResults([]);
                setAvailableTags([]);
                setTotalPages(1);
            }
        };

        fetchSearchResults();
        console.log(`Query: ${queryFromUrl}, Page: ${currentPage}`);
    }, [queryFromUrl, currentPage]);

    // Handle tag selection for filtering
    const toggleTagSelection = (tag) => {
        setSelectedTags((prevSelectedTags) =>
            prevSelectedTags.includes(tag) ? prevSelectedTags.filter((t) => t !== tag) : [...prevSelectedTags, tag]
        );
    };

    // Filter results based on selected tags
    useEffect(() => {
        if (selectedTags.length === 0) {
            setFilteredResults(results);
        } else {
            const filtered = results.filter((item) => selectedTags.every((tag) => item.tags.includes(tag)));
            setFilteredResults(filtered);
        }
    }, [selectedTags, results]);

    const closeTagEditor = () => {
        setSelectedUuid(null);
    };

    // Generate pagination buttons
    const getPaginationButtons = () => {
        const buttons = [];
        const maxButtons = 5;
        let startPage = Math.max(currentPage - Math.floor(maxButtons / 2), 1);
        let endPage = startPage + maxButtons - 1;

        if (endPage > totalPages) {
            endPage = totalPages;
            startPage = Math.max(endPage - maxButtons + 1, 1);
        }

        for (let page = startPage; page <= endPage; page++) {
            buttons.push(
                <button
                    key={page}
                    className={`btn btn-sm ${page === currentPage ? 'btn-active' : 'btn-outline'}`}
                    onClick={() => handlePageChange(page)}
                >
                    {page}
                </button>
            );
        }

        return buttons;
    };

    const handlePageChange = (page) => {
        if (page < 1 || page > totalPages) return;
        setCurrentPage(page);
        setSearchParams({ q: query, page: page });
    };

    return (
        <div className="p-4">
            {/* Search Bar */}
            <div className="flex mb-4">
                <input
                    type="text"
                    placeholder="Search..."
                    className="input input-bordered w-full"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSearch();
                    }}
                />
                <button className="btn btn-primary ml-2" onClick={handleSearch}>
                    Search
                </button>
            </div>

            {/* Tag Filter Dropdown */}
            {availableTags.length > 0 && (
                <div className="relative inline-block text-left" ref={dropdownRef}>
                    <div>
                        <button
                            type="button"
                            className="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none"
                            onClick={() => setDropdownOpen(!dropdownOpen)}
                        >
                            Filter by Tags
                            <svg
                                className="-mr-1 ml-2 h-5 w-5"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                                aria-hidden="true"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.25 8.27a.75.75 0 01-.02-1.06z"
                                    clipRule="evenodd"
                                />
                            </svg>
                        </button>
                    </div>

                    {/* Dropdown Menu */}
                    {dropdownOpen && (
                        <div className="origin-top-left absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
                            <div
                                className="py-1 max-h-60 overflow-y-auto"
                                role="menu"
                                aria-orientation="vertical"
                                aria-labelledby="options-menu"
                            >
                                {availableTags.map((tag) => (
                                    <label
                                        key={tag}
                                        className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer"
                                    >
                                        <input
                                            type="checkbox"
                                            className="mr-2"
                                            checked={selectedTags.includes(tag)}
                                            onChange={() => toggleTagSelection(tag)}
                                        />
                                        {tag}
                                    </label>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Loading Indicator */}
            {loading && (
                <div className="flex justify-center items-center mt-4">
                    <span className="loading loading-spinner loading-lg"></span>
                </div>
            )}

            {/* Search Results */}
            {!loading && filteredResults.length > 0 && (
                <>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                        {filteredResults.map((item) => (
                            <div key={item.uuid} className="card bg-base-100 shadow-md">
                                <figure>
                                    <img
                                        src={item.thumbnail_url}
                                        alt={item.title}
                                        className="w-full h-48 object-cover"
                                    />
                                </figure>
                                <div className="card-body">
                                    <h2 className="card-title text-sm">{item.title}</h2>
                                    <p className="text-xs text-gray-600">
                                        Tags:{' '}
                                        {item.tags.length > 3
                                            ? `${item.tags.slice(0, 3).join(', ')}, ...`
                                            : item.tags.join(', ')}
                                    </p>
                                    <div className="card-actions justify-end space-x-2 mt-2">
                                        <button
                                            className="btn btn-xs btn-outline"
                                            onClick={() => window.open(item.url, '_blank')}
                                        >
                                            Open In Dropbox
                                        </button>

                                        <button
                                            className="btn btn-xs btn-outline"
                                            onClick={() => {
                                                setSelectedUuid(item.uuid);
                                                setSelectedTags(item.tags);
                                            }}
                                        >
                                            Edit Tags
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Pagination Controls */}
                    <div className="flex justify-center items-center mt-6 space-x-2">
                        {/* Previous Button */}
                        <button
                            className="btn btn-sm btn-outline"
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                        >
                            Previous
                        </button>

                        {/* Page Number Buttons */}
                        {getPaginationButtons()}

                        {/* Next Button */}
                        <button
                            className="btn btn-sm btn-outline"
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                        >
                            Next
                        </button>
                    </div>
                </>
            )}

            {/* No Results Message */}
            {!loading && filteredResults.length === 0 && query && (
                <div className="mt-4 text-center">
                    <p className="text-gray-500">No results found for "{query}".</p>
                </div>
            )}

            {/* Tag Editor Modal */}
            {selectedUuid && <TagEditor uuid={selectedUuid} onClose={closeTagEditor} tags={selectedTags} />}
        </div>
    );
}

export default Search;
