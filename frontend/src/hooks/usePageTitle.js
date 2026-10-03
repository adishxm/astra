import { useEffect } from 'react';

/**
 * Sets the document title to "<title> | ASTRA"
 * @param {string} title
 */
export function usePageTitle(title) {
  useEffect(() => {
    if (title) {
      document.title = `${title} | ASTRA`;
    }
  }, [title]);
}
