import React, { useState, useEffect } from 'react';
import { Mail, ArrowUp, ExternalLink } from 'lucide-react';
import { SiGithub } from 'react-icons/si';
import { Linkedin } from 'lucide-react';
import { Link } from "react-router-dom";  // ✅ Added for internal routing
import loggd from './Autd.svg';
import rockt from './itop.svg';

const Footer = () => {
    const [showScrollTop, setShowScrollTop] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setShowScrollTop(window.scrollY > 500);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <footer className="relative bg-gradient-to-br from-blue-900 via-purple-900 to-slate-900 border-t border-slate-700 overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl"></div>
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/90 via-purple-900/90 to-slate-900/90"></div>
            </div>

            <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
                {/* Main Footer Content */}
                <div className="py-16">
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                        {/* Brand Section */}
                        <div className="lg:col-span-5">
                            <div className="flex items-center space-x-4 mb-8">
                                <div>
                                    <div className="mb-1">
                                        <img src={loggd} alt="AutoEDA Logo" className="h-10 w-auto block dark:hidden" />
                                        <img src={loggd} alt="AutoEDA Logo" className="h-10 w-auto hidden dark:block" />
                                    </div>
                                    <p className="text-slate-300 font-medium tracking-wide">
                                        Automated Exploratory Data Analysis
                                    </p>
                                </div>
                            </div>

                            <p className="text-slate-300 text-lg leading-relaxed mb-8 max-w-lg">
                                <span className="font-semibold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Instant insights, zero hassle.</span>
                                <br />
                                Empower your data journey with our automated analysis platform.
                            </p>
                        </div>

                        {/* Links Section */}
                        <div className="lg:col-span-7">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                                {/* Company Section */}
                                <div>
                                    <h4 className="text-lg font-bold text-white mb-6 relative">
                                        Company
                                        <div className="absolute -bottom-2 left-0 w-12 h-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full"></div>
                                    </h4>
                                    <ul className="space-y-3">
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                About Us
                                            </a>
                                        </li>
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                Our Team
                                            </a>
                                        </li>
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                Events
                                            </a>
                                        </li>
                                    </ul>
                                </div>

                                {/* Support Section */}
                                <div>
                                    <h4 className="text-lg font-bold text-white mb-6 relative">
                                        Support
                                        <div className="absolute -bottom-2 left-0 w-12 h-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full"></div>
                                    </h4>
                                    <ul className="space-y-3">
                                        <li>
                                            <Link to="/contact" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                Contact Us
                                            </Link>
                                        </li>
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                FAQ
                                            </a>
                                        </li>
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                Community
                                            </a>
                                        </li>
                                    </ul>
                                </div>

                                {/* Legal Section */}
                                <div>
                                    <h4 className="text-lg font-bold text-white mb-6 relative">
                                        Legal
                                        <div className="absolute -bottom-2 left-0 w-12 h-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full"></div>
                                    </h4>
                                    <ul className="space-y-3">
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                Privacy Policy
                                            </a>
                                        </li>
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                Terms of Service
                                            </a>
                                        </li>
                                        <li>
                                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                                Cookie Policy
                                            </a>
                                        </li>
                                    </ul>
                                </div>

                                {/* Contact Section */}
                                <div>
                                    <h4 className="text-lg font-bold text-white mb-6 relative">
                                        Contact
                                        <div className="absolute -bottom-2 left-0 w-12 h-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full"></div>
                                    </h4>
                                    <div className="space-y-4">
                                        <div className="flex items-start space-x-4 text-slate-300 hover:text-blue-300 transition-colors duration-300">
                                            <Mail className="w-5 h-5 text-blue-300 mt-1 flex-shrink-0" />
                                            <a href="mailto:satyapriyanidhi@gmail.com" className="font-medium hover:underline">
                                                Email
                                            </a>
                                        </div>
                                        <div className="flex items-start space-x-4 text-slate-300 hover:text-blue-300 transition-colors duration-300">
                                            <SiGithub className="w-5 h-5 text-blue-300 mt-1 flex-shrink-0" />
                                            <a href="https://github.com/Nidhi-Satyapriya/AutoEDA-Automated-Data-Preprocessing-Toolkit" className="font-medium hover:underline">
                                                GitHub
                                            </a>
                                        </div>
                                        <div className="flex items-start space-x-4 text-slate-300 hover:text-blue-300 transition-colors duration-300">
                                            <Linkedin className="w-5 h-5 text-blue-300 mt-1 flex-shrink-0" />
                                            <a href="https://www.linkedin.com/in/nidhi-satyapriya-960556249/" className="font-medium hover:underline">
                                                LinkedIn
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bottom Footer */}
                <div className="py-6 border-t border-slate-700/50">
                    <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
                        <div className="text-slate-400 order-2 md:order-1">
                            © 2025 AutoEDA. All rights reserved.
                        </div>

                        <div className="flex items-center space-x-8 order-1 md:order-2">
                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                Privacy Policy
                            </a>
                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                Terms of Service
                            </a>
                            <a href="#" className="text-slate-300 hover:text-blue-300 transition-colors duration-300 font-medium">
                                Cookie Policy
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            {/* Scroll to Top Button */}
            {showScrollTop && (
                <button
                    onClick={scrollToTop}
                    className="fixed bottom-8 right-8 p-4 hover:shadow-purple-500/50 hover:scale-110 transition-all duration-300 z-50 group"
                >
                    <img
                        src={rockt}
                        alt="Scroll to top"
                        className="w-12 h-12 group-hover:scale-110 transition-transform duration-300"
                    />
                </button>
            )}
        </footer>
    );
};

export default Footer;
