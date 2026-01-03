import { useEffect, useRef } from 'react';
import { tokenStream, systemTemperature } from './state/signals';

export const HearthEditor = () => {
    const editorRef = useRef<HTMLDivElement>(null);

    // Direct DOM manipulation for high-frequency updates
    // Bypasses React Reconciliation
    useEffect(() => {
        return tokenStream.subscribe((delta) => {
             if (editorRef.current) {
                 // Append text directly to the DOM node
                 editorRef.current.innerText += delta;
                 
                 // Auto-scroll logic if "Locked" to bottom
                 scrollToCaret(); 
             }
        });
    }, []);

    return (
        <div className="layout-container">
            <div className={`hearth-glow ${systemTemperature.value}`} />
            
            <div 
                ref={editorRef}
                contentEditable 
                className="typography-serif focus:outline-none max-w-2xl mx-auto" 
            />
        </div>
    );
};