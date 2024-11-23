import SearchBar from '@/components/Searchbar'
import UploadIcon from '@/icons/UploadIcon'
import LogoutIcon from '@/icons/LogoutIcon'
import PencilIcon from '@/icons/PencilIcon'

function App() {
  const isAuthenticated = true;
  const pressedSearch = true;

  return (
    <div className='bg-base-100'>

      {/* if logged in */}
      {isAuthenticated && (
        <>

        {/* if logged in */}
        {pressedSearch && (
          <>
            <div className='container mx-auto max-w-6xl'>
                <div className='row-start-1 row-span-1 col-start-1 h-16 mt-6 col-span-12 grid grid-cols-6'>
                  <div className='text-center font-grotesk font-bold text-2xl text-primary mt-1'>PixQuery</div>
                  <div className='col-span-4 h-4/6'><SearchBar height='h-full'/></div>
                  <div className='col-start-6 grid grid-cols-4 gap-2 mt-2'>
                    <UploadIcon className='col-start-3'/>
                    <LogoutIcon />
                  </div>
                </div>
            </div>
            <div className="divider h-px"></div>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mx-2'>
                {/* search results */}

                <div className='text-sm max-h-48'>
                  <img className='rounded-lg' src='https://static0.gamerantimages.com/wordpress/wp-content/uploads/2023/02/aoi-todo.jpg' />
                  <div className='font-semibold mt-2'>Todo Angry</div> 
                  <div className='grid-cols-8 grid gap-2'>
                    <div className='col-span-7 truncate'><span className='font-semibold'>Tags: </span>Todo, Jujutsu Kaisen, Angry, Zone ...</div> 
                    <div className='justify-items-end'><PencilIcon className='h-4 w-4 justify-items-end'/></div>
                  </div>
                </div>

                <div className='text-sm max-h-48'>
                  <img className='rounded-lg w-full h-5/6 object-cover' src={'https://preview.redd.it/this-guy-todo-aoi-would-be-so-amazing-in-real-life-its-crazy-v0-re8ime34w61d1.jpeg?auto=webp&s=1d288e566947b6d75ed2a0ec9aed89173b220f5a'} />
                  <div className='font-semibold mt-2'>Todo Angry</div> 
                  <div className='grid-cols-8 grid gap-2'>
                    <div className='col-span-7 truncate'><span className='font-semibold'>Tags: </span>Todo, Jujutsu Kaisen, Angry, Zone ...</div> 
                    <div className='justify-items-end'><PencilIcon className='h-4 w-4 justify-items-end'/></div>
                  </div>
                </div>

                {Array.from({ length: 20 }).map((_, index) => (
                  <div key={index} className='text-sm'>
                    <img className='rounded-lg' src='https://static0.gamerantimages.com/wordpress/wp-content/uploads/2023/02/aoi-todo.jpg' />
                    <div className='font-semibold mt-2'>Todo Angry</div>
                    <div className='grid-cols-8 grid gap-2'>
                      <div className='col-span-7 truncate'>
                        <span className='font-semibold'>Tags: </span>Todo, Jujutsu Kaisen, Angry, Zone ...
                      </div>
                      <div className='justify-items-end'>
                        <PencilIcon className='h-4 w-4 justify-items-end'/>
                      </div>
                    </div>
                  </div>
                ))}

            </div>

          </>

        )}

        {!pressedSearch && (
          <div className='container mx-auto max-w-7xl h-svh overflow-hidden'>
            <div className='grid md:grid-cols-12 grid-cols-4 grid-rows-5 gap-4 h-full mt-4'>
              <div className='row-start-1 col-start-4 col-span-1 md:col-start-11 md:col-span-2 lg:col-span-1 lg:col-start-12 justify-items-end lg:mr-4 mr-2 flex flex-row-reverse grid grid-cols-2 gap-6'>
                <UploadIcon />
                <LogoutIcon />
              </div>

              <div className='row-start-2 flex flex-col-reverse row-span-1 col-start-1 col-span-4 md:col-span-6 md:col-start-4 text-center font-grotesk font-bold text-6xl text-primary'>PixQuery</div>


              <div className='row-start-3 row-span-1 col-start-1 col-span-4 md:col-span-8 md:col-start-3 justify-items-center font-grotesk font-bold text-6xl text-primary'>
                  <SearchBar height={'h-1/3'}/>
              </div>
            </div>
          </div>
        )}
        </>
      )}
    </div>
  )
}

export default App
