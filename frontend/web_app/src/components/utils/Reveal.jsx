import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export default function Reveal({ children }) {
  return (
    <div>
        <motion.div
          variants={{
            hidden: { opacity: 0, y: 75 },
            visible: { opacity: 1, y: 0 }
          }}
          initial="hidden"
          animate="visible"
          transition={{ duration:0.25, ease: 'easeInOut' }}
        >
          {children}
        </motion.div>
    </div>
  );
}
