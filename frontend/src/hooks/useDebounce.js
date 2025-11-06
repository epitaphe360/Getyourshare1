import { useState, useEffect } from 'react';

/**
 * Custom hook for debouncing values
 * 
 * Delays updating the value until after the specified delay
 * Useful for search inputs, resize handlers, etc.
 * 
 * @param {any} value - Value to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {any} Debounced value
 */
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // Set up timeout
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Clean up timeout on value change or unmount
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Custom hook for debounced callback
 * 
 * Returns a memoized callback that is debounced
 * 
 * @param {Function} callback - Callback to debounce
 * @param {number} delay - Delay in milliseconds
 * @param {Array} dependencies - Dependency array
 * @returns {Function} Debounced callback
 */
export const useDebouncedCallback = (callback, delay = 500, dependencies = []) => {
  const [timeoutId, setTimeoutId] = useState(null);

  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [timeoutId]);

  const debouncedCallback = (...args) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    const id = setTimeout(() => {
      callback(...args);
    }, delay);

    setTimeoutId(id);
  };

  return debouncedCallback;
};

/**
 * Hook pour protéger contre les doubles-clics sur les boutons
 * Empêche l'exécution multiple d'actions pendant qu'une est en cours
 * 
 * @param {Function} callback - Fonction à exécuter
 * @param {number} minInterval - Intervalle minimum entre 2 exécutions en ms (défaut: 300ms)
 * @returns {Object} { execute, isExecuting, reset }
 * 
 * @example
 * const { execute: handleSave, isExecuting } = useClickProtection(async () => {
 *   await api.post('/save');
 * });
 * 
 * <button onClick={handleSave} disabled={isExecuting}>
 *   {isExecuting ? "Enregistrement..." : "Enregistrer"}
 * </button>
 */
export const useClickProtection = (callback, minInterval = 300) => {
  const [isExecuting, setIsExecuting] = useState(false);
  const lastExecutionRef = useState(0);

  const execute = async (...args) => {
    const now = Date.now();
    
    // Vérifier si en cours d'exécution
    if (isExecuting) {
      console.log('⚠️ Action déjà en cours, double-clic ignoré');
      return;
    }

    // Vérifier intervalle minimum
    if (now - lastExecutionRef.current < minInterval) {
      console.log('⚠️ Clic trop rapide, ignoré');
      return;
    }

    setIsExecuting(true);
    lastExecutionRef.current = now;

    try {
      await callback(...args);
    } catch (error) {
      console.error('❌ Erreur lors de l\'exécution:', error);
      throw error;
    } finally {
      setIsExecuting(false);
    }
  };

  const reset = () => {
    setIsExecuting(false);
    lastExecutionRef.current = 0;
  };

  return { execute, isExecuting, reset };
};

/**
 * Hook pour navigation protégée contre double-clic
 * 
 * @param {Function} navigate - React Router navigate function
 * @returns {Function} Fonction de navigation protégée
 * 
 * @example
 * import { useNavigate } from 'react-router-dom';
 * const safeNavigate = useNavigateProtection(navigate);
 * 
 * <button onClick={() => safeNavigate('/dashboard')}>Tableau de bord</button>
 */
export const useNavigateProtection = (navigate) => {
  const [isNavigating, setIsNavigating] = useState(false);

  const safeNavigate = (path, options = {}) => {
    if (isNavigating) {
      console.log('⚠️ Navigation déjà en cours, clic ignoré');
      return;
    }

    setIsNavigating(true);
    
    // Reset après 500ms
    setTimeout(() => setIsNavigating(false), 500);
    
    navigate(path, options);
  };

  return safeNavigate;
};

export default useDebounce;
