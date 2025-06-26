import React, { useState } from "react";
import { motion } from "framer-motion";

const Contact = () => {
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setSubmitted(true);
    };

    return (
        <motion.div
            className="container mx-auto px-4 py-16 max-w-2xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <h2 className="text-3xl font-bold text-center mb-4 text-emerald-600 dark:text-emerald-400">Leave a Review</h2>
            <p className="text-gray-600 dark:text-slate-400 text-center mb-6">
                We value your feedback! Share your experience with AutoEDA.
            </p>

            {submitted ? (
                <div className="p-4 bg-emerald-100 dark:bg-emerald-700 text-emerald-800 dark:text-white rounded-xl text-center shadow-lg">
                    Message submitted successfully! Thank you for reaching out.
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-[#111827] p-6 rounded-xl shadow-xl">
                    <div>
                        <label className="block text-gray-700 dark:text-gray-200 mb-2 font-medium">Name</label>
                        <input
                            type="text"
                            placeholder="Your name"
                            required
                            className="w-full p-3 border border-gray-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-900 dark:text-gray-50 bg-white dark:bg-slate-800 placeholder-gray-400 dark:placeholder-slate-400"
                        />
                    </div>

                    <div>
                        <label className="block text-gray-700 dark:text-gray-200 mb-2 font-medium">Email</label>
                        <input
                            type="email"
                            placeholder="Your email"
                            required
                            className="w-full p-3 border border-gray-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-900 dark:text-gray-50 bg-white dark:bg-slate-800 placeholder-gray-400 dark:placeholder-slate-400"
                        />
                    </div>

                    <div>
                        <label className="block text-gray-700 dark:text-gray-200 mb-2 font-medium">Type</label>
                        <select
                            required
                            className="w-full p-3 border border-gray-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-900 dark:text-gray-50 bg-white dark:bg-slate-800 placeholder-gray-400 dark:placeholder-slate-400"
                        >
                            <option value="" disabled selected>Select an option</option>
                            <option value="Feedback">Feedback</option>
                            <option value="Bug Report">Bug Report</option>
                            <option value="Feature Request">Feature Request</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-gray-700 dark:text-gray-200 mb-2 font-medium">Message</label>
                        <textarea
                            placeholder="Your message..."
                            required
                            rows={4}
                            className="w-full p-3 border border-gray-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-900 dark:text-gray-50 bg-white dark:bg-slate-800 placeholder-gray-400 dark:placeholder-slate-400"
                        ></textarea>
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-emerald-500 hover:bg-emerald-600 text-white py-3 rounded-lg transition shadow-md flex justify-center items-center space-x-2"
                    >
                        <span>🚀 Submit</span>
                    </button>
                </form>
            )}
        </motion.div>
    );
};

export default Contact;
