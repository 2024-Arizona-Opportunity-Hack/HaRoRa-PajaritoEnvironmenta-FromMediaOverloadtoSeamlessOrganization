import PencilIcon from '@/icons/PencilIcon'

export default function ImageCard({ src, title, tags }) {
  const tag_string = tags.join(', ');

  return (
    <div className='text-sm max-h-48'>
      <img className='rounded-lg w-full h-5/6 object-cover hover:scale-105 active:scale-95 hover:cursor-pointer' src={src} />
      <div className='font-semibold mt-2'>{title}</div> 
      <div className='grid-cols-8 grid gap-2'>
        <div className='col-span-7 truncate'><span className='font-semibold'>Tags: </span>{tag_string}</div> 
        <div className='justify-items-end'><PencilIcon className='h-4 w-4 hover:cursor-pointer hover:scale-105 active:scale-105'/></div>
      </div>
    </div>
  )
}
