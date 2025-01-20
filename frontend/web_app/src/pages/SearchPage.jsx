// src/pages/SearchPage.jsx
import React from 'react';
import Search from '../components/Search';
import Reveal from '../components/utils/Reveal.jsx';

function SearchPage() {
    return (
        <Reveal>
            <div className="p-4 text-primary max-w-6xl mx-auto">
                <div className="p4">
                    <Search />
                </div>
            </div>
        </Reveal>
    );
}

export default SearchPage;
