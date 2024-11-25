import { useState, useEffect } from 'react';
import SearchBar from '@/components/Searchbar'
import ImageCard from '@/components/ImageCard'
import UploadIcon from '@/icons/UploadIcon'
import LogoutIcon from '@/icons/LogoutIcon'
import PencilIcon from '@/icons/PencilIcon'
import { getProfileInfo, handleLogin, searchMedia } from '@/api.js'

function App() {
  //const pressedSearch = false;
  const [userProfile, setUserProfile] = useState(null);
  const [query, setQuery] = useState('');
  const [pressedSearch, setPressedSearch] = useState(false);
  const [showResultsPage, setShowResultsPage] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const response = await getProfileInfo();
        if (response && response.response) {
          setUserProfile(response.response);
        } else {
          setUserProfile(null);
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        setUserProfile(null);
      }
    };

    checkAuthentication();
  }, []);

  // create a effect that runs when pressedSearch is set to true
  // it will call searchMedia func
  useEffect(() => {
    const performSearch = async () => {
      if (pressedSearch) {
        setShowResultsPage(true)
        try {
          const results = await searchMedia(query);
          console.log(results.results)
          setSearchResults(results.results);
        } catch (error) {
          console.error('Error searching media:', error);
          setSearchResults([]);
        }
        setPressedSearch(false);
      }
    };

    performSearch();
  }, [pressedSearch, query]);


  return (
    <div className='bg-base-100'>

      {/* if logged in */}
      {userProfile && (
        <>

        {/* if logged in */}
        {showResultsPage && (
          <>
            <div className='container mx-auto max-w-6xl'>
                <div className='row-start-1 row-span-1 col-start-1 h-16 mt-6 col-span-12 grid grid-cols-6'>
                  <div className='text-center font-grotesk font-bold text-2xl text-primary mt-1'>PixQuery</div>
                  <div className='col-span-4 h-4/6'><SearchBar query={query} setQuery={setQuery} setPressedSearch={setPressedSearch} height='h-full'/></div>
                  <div className='col-start-6 grid grid-cols-4 gap-2 mt-2'>
                    <UploadIcon className='col-start-3'/>
                    <LogoutIcon />
                  </div>
                </div>
            </div>
            <div className="divider h-px"></div>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mx-3'>
                {/* search results */}
                {searchResults === null ? (
                  <div className="col-span-full text-center">Loading...</div>
                ) : searchResults.length === 0 ? (
                  <div className="col-span-full text-center">No results for "{query}"</div>
                ) : (
                  searchResults.map((result, index) => (
                    <ImageCard
                      key={index}
                      src={result.thumbnail_url}
                      dropbox_url={result.url}
                      title={result.title}
                      tags={result.tags}
                    />
                  ))
                )}
            </div>

          </>

        )}

        {!showResultsPage && (
          <div className='container mx-auto max-w-7xl h-svh overflow-hidden'>
            <div className='grid md:grid-cols-12 grid-cols-4 grid-rows-5 gap-4 h-full mt-4'>
              <div className='row-start-1 col-start-4 col-span-1 md:col-start-11 md:col-span-2 lg:col-span-1 lg:col-start-12 justify-items-end lg:mr-4 mr-2 flex flex-row-reverse grid grid-cols-2 gap-6'>
                <UploadIcon />
                <LogoutIcon />
              </div>

              <div className='row-start-2 flex flex-col-reverse row-span-1 col-start-1 col-span-4 md:col-span-6 md:col-start-4 text-center font-grotesk font-bold text-6xl text-primary'>PixQuery</div>


              <div className='row-start-3 row-span-1 col-start-1 col-span-4 md:col-span-8 md:col-start-3 justify-items-center font-grotesk font-bold text-6xl text-primary'>
                  <SearchBar query={query} setQuery={setQuery} setPressedSearch={setPressedSearch} height={'h-1/3'}/>
              </div>
            </div>
          </div>
        )}
        </>
      )}

      {!userProfile && (
        <div className='btn' onClick={handleLogin}>Login</div>
      )}
    </div>
  )
}

export default App
