import { useState, useEffect, useRef } from 'react';
import { handleLogout } from '@/api.js'

export default function Avatar({ initials, top_pos }) {
  const [isOpen, setIsOpen] = useState(false);
  const top_class = top_pos ? top_pos : 'top-1/4'
  const menuRef = useRef(null);

  function handleAvatarClick() {
    setIsOpen(prevVal => !prevVal);
  }

  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuRef]);

  return (
    <div ref={menuRef} className="relative flex flex-col items-end">
      <div
        className={"avatar placeholder cursor-pointer hover:scale-105 active:scale-95 "}
        onClick={handleAvatarClick}
      >
        <div className="bg-neutral text-neutral-content w-8 h-8 rounded-full">
          <span className="text-xs font-grotesk font-medium">{initials}</span>
        </div>
      </div>
      {isOpen && (
        <ul className={top_class + " absolute right-0 lg:mt-2 menu dropdown-content bg-base-100 rounded-box z-[1] w-52 shadow"}>
          <li onClick={handleLogout}>
            <a>Logout</a>
          </li>
        </ul>
      )}
    </div>
  );
}

