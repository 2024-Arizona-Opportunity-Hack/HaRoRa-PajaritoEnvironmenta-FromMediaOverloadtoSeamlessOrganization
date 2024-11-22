import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Reveal from '../components/utils/Reveal.jsx';
//import { getProfileInfo } from '../api/api';
import { getProfileInfo, handleLogout, handleLogin } from '../api/api'; // Import the necessary API functions

function Navbar() {
    const [theme, setTheme] = useState('formalLight');
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const checkAuth = async () => {
            const { response, err } = await getProfileInfo();
            setIsAuthenticated(!err);
        };

        checkAuth();
    }, []);
    const handleLogoutClick = async () => {
        await handleLogout(); // Log out the user
        window.location.reload(); // Refresh the page to reset the authentication state
    };
    return (

        <Reveal>
            <div className="navbar shadow-md h-4 bg-neutral text-primary mx-14 rounded-full" style={{width: 'auto'}}>
                {/* Brand */}
                <div className="flex-1 ml-8">
                    <Link
                        to="/"
                        className="font-grotesk text-xl font-bold transition duration-300 ease-in-out"
                    >
                        PixQuery
                    </Link>
                </div>
                <div className="flex-none mr-8">
                    <ul className="menu menu-horizontal px-1">
                      {isAuthenticated ? (
                            <>

                              <li><a href='/upload' className=''>
                                    <svg className='w-6 h-6' xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M246.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 109.3 192 320c0 17.7 14.3 32 32 32s32-14.3 32-32l0-210.7 73.4 73.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128zM64 352c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 64c0 53 43 96 96 96l256 0c53 0 96-43 96-96l0-64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 64c0 17.7-14.3 32-32 32L96 448c-17.7 0-32-14.3-32-32l0-64z"/></svg>
                              </a></li>
                              <li><a href='/search'>Search</a></li>
                              <li>
                                <a onClick={handleLogoutClick} className='bg-primary rounded-full text-base-100 hover:bg-primary hover:scale-105 active:scale-95 active:bg-primary'>
                                    Logout
                                </a>
                              </li>
                            </>
                        ) : (
                          <li><a onClick={handleLogin} className='bg-primary rounded-full text-base-100 hover:bg-primary hover:scale-105 active:scale-95 active:bg-primary'>Login</a></li>
                        )
                      }
                    </ul>
                </div>
            </div>
        </Reveal>

    );
}

export default Navbar;
