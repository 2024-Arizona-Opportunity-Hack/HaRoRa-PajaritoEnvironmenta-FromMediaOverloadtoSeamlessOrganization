// src/components/Navbar.jsx
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getProfileInfo } from '../api/api';

function Navbar() {
  const [theme, setTheme] = useState('light');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleThemeChange = (e) => {
    setTheme(e.target.value);
    document.documentElement.setAttribute('data-theme', e.target.value);
  };

  useEffect(() => {
    const checkAuth = async () => {
      const { response, err } = await getProfileInfo();
      setIsAuthenticated(!err);
    };

    checkAuth();
  }, []);

  return (
    <nav className="bg-base-100 shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        {/* Brand */}
        <Link
          to="/"
          className="text-3xl font-bold text-primary hover:text-primary-focus transition duration-300 ease-in-out"
        >
          PEEC's Media Manager
        </Link>

        {/* Navigation Links and Theme Selector */}
        <div className="flex items-center space-x-6">
          {isAuthenticated && (
            <>
              <Link
                to="/upload"
                className="btn btn-outline btn-primary"
              >
                Upload
              </Link>
              <Link
                to="/search"
                className="btn btn-outline btn-primary"
              >
                Search
              </Link>
            </>
          )}
          <select
            className="select select-bordered bg-base-100 text-base-content py-2 px-4 rounded-md shadow-md focus:outline-none"
            value={theme}
            onChange={handleThemeChange}
          >
            <option value="nord">Light Mode</option>
            <option value="luxury">Dark Mode</option>
          </select>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
