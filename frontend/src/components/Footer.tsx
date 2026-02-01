import React from 'react';

const Footer: React.FC = () => {
    return (
        <footer className="relative z-10 py-6 mt-auto">
            <div className="container mx-auto px-4 text-center">
                <p className="text-white/40 text-xs tracking-widest uppercase font-medium">
                    &copy; {new Date().getFullYear()} Nataraj EL. All Rights Reserved.
                </p>
            </div>
        </footer>
    );
};

export default Footer;
