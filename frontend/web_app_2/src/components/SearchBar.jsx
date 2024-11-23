export default function SearchBar({ height }) {
  return (
    <label className={'w-9/12 rounded-full flex flex-row border bg-white px-3 ' + height}>
      {/* search icon */}
        <svg className='h-6 w-6 my-auto hover:cursor-pointer hover:scale-105 active:scale-95' xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/></svg>

      {/* input query box */}
        <input type='text' className='w-full focus:outline-none placeholder:text-secondary placeholder:text-sm placeholder:font-normal bg-white font-normal text-sm rounded-full grow focus:ring-0 focus:border-0 active:ring-0 active:border-0 mx-2 px-2' placeholder='Search'/>

      {/* camera icon */}
        <svg className='h-6 w-6 my-auto hover:cursor-pointer hover:scale-105 active:scale-95' xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M149.1 64.8L138.7 96 64 96C28.7 96 0 124.7 0 160L0 416c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-256c0-35.3-28.7-64-64-64l-74.7 0L362.9 64.8C356.4 45.2 338.1 32 317.4 32L194.6 32c-20.7 0-39 13.2-45.5 32.8zM256 192a96 96 0 1 1 0 192 96 96 0 1 1 0-192z"/></svg>
    </label>
  )
};
