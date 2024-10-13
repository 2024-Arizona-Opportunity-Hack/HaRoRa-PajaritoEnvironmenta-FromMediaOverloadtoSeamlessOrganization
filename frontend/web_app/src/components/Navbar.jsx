// src/components/Navbar.jsx
import { Link } from 'react-router-dom';
import { useState } from 'react';

function Navbar() {
  const [theme, setTheme] = useState('light');

  const handleThemeChange = (e) => {
    setTheme(e.target.value);
    document.documentElement.setAttribute('data-theme', e.target.value);
  };

  return (
    <nav className="bg-base-100 shadow">
      <div className="container mx-auto px-4 py-2 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-primary">
          PEEC's Media Manager
        </Link>
        <div className="flex items-center space-x-4">
          <Link to="/" className="btn btn-outline btn-primary">
            Upload
          </Link>
          <Link to="/search" className="btn btn-outline btn-primary">
            Search
          </Link>
          <select
            className="select select-bordered"
            value={theme}
            onChange={handleThemeChange}
          >
            <option value="nord">Light</option>

            <option value="luxury">Dark</option>
            

          </select>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
