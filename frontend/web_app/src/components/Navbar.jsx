// components/Navbar.jsx
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-base-100 shadow">
      <div className="container mx-auto px-4 py-2 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">
          Media Manager
        </Link>
        <div>
          <Link to="/" className="btn btn-ghost">
            Upload
          </Link>
          <Link to="/search" className="btn btn-ghost">
            Search
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
