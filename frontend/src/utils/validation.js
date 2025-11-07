/**
 * Validation Helpers - Validation côté client avant envoi API
 * Réduit les erreurs API et améliore l'UX avec feedback immédiat
 */

/**
 * Valide un email
 */
export const validateEmail = (email) => {
  if (!email) {
    return { valid: false, error: "L'email est requis" };
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, error: "Format d'email invalide" };
  }
  
  return { valid: true };
};

/**
 * Valide un mot de passe
 */
export const validatePassword = (password, options = {}) => {
  const {
    minLength = 8,
    requireUppercase = true,
    requireLowercase = true,
    requireNumber = true,
    requireSpecial = false
  } = options;
  
  if (!password) {
    return { valid: false, error: "Le mot de passe est requis" };
  }
  
  if (password.length < minLength) {
    return { 
      valid: false, 
      error: `Le mot de passe doit contenir au moins ${minLength} caractères` 
    };
  }
  
  if (requireUppercase && !/[A-Z]/.test(password)) {
    return { 
      valid: false, 
      error: "Le mot de passe doit contenir au moins une majuscule" 
    };
  }
  
  if (requireLowercase && !/[a-z]/.test(password)) {
    return { 
      valid: false, 
      error: "Le mot de passe doit contenir au moins une minuscule" 
    };
  }
  
  if (requireNumber && !/[0-9]/.test(password)) {
    return { 
      valid: false, 
      error: "Le mot de passe doit contenir au moins un chiffre" 
    };
  }
  
  if (requireSpecial && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return { 
      valid: false, 
      error: "Le mot de passe doit contenir au moins un caractère spécial" 
    };
  }
  
  return { valid: true };
};

/**
 * Valide que les mots de passe correspondent
 */
export const validatePasswordMatch = (password, confirmPassword) => {
  if (password !== confirmPassword) {
    return { valid: false, error: "Les mots de passe ne correspondent pas" };
  }
  return { valid: true };
};

/**
 * Valide un numéro de téléphone
 */
export const validatePhone = (phone) => {
  if (!phone) {
    return { valid: false, error: "Le numéro de téléphone est requis" };
  }
  
  // Format: +212XXXXXXXXX ou 0XXXXXXXXX
  const phoneRegex = /^(\+212|0)[5-7][0-9]{8}$/;
  if (!phoneRegex.test(phone.replace(/\s/g, ''))) {
    return { 
      valid: false, 
      error: "Format de téléphone invalide (ex: +212612345678)" 
    };
  }
  
  return { valid: true };
};

/**
 * Valide un montant
 */
export const validateAmount = (amount, options = {}) => {
  const { min = 0, max = Infinity, required = true } = options;
  
  if (required && (amount === null || amount === undefined || amount === '')) {
    return { valid: false, error: "Le montant est requis" };
  }
  
  const numAmount = parseFloat(amount);
  
  if (isNaN(numAmount)) {
    return { valid: false, error: "Le montant doit être un nombre" };
  }
  
  if (numAmount < min) {
    return { 
      valid: false, 
      error: `Le montant doit être supérieur ou égal à ${min}€` 
    };
  }
  
  if (numAmount > max) {
    return { 
      valid: false, 
      error: `Le montant ne peut pas dépasser ${max}€` 
    };
  }
  
  return { valid: true, value: numAmount };
};

/**
 * Valide un champ requis
 */
export const validateRequired = (value, fieldName = "Ce champ") => {
  if (value === null || value === undefined || value === '' || 
      (Array.isArray(value) && value.length === 0)) {
    return { valid: false, error: `${fieldName} est requis` };
  }
  return { valid: true };
};

/**
 * Valide une URL
 */
export const validateURL = (url) => {
  if (!url) {
    return { valid: false, error: "L'URL est requise" };
  }
  
  try {
    new URL(url);
    return { valid: true };
  } catch (e) {
    return { valid: false, error: "Format d'URL invalide" };
  }
};

/**
 * Valide une longueur de texte
 */
export const validateLength = (text, options = {}) => {
  const { min = 0, max = Infinity, fieldName = "Ce champ" } = options;
  
  if (!text) {
    return { valid: false, error: `${fieldName} est requis` };
  }
  
  const length = text.length;
  
  if (length < min) {
    return { 
      valid: false, 
      error: `${fieldName} doit contenir au moins ${min} caractères` 
    };
  }
  
  if (length > max) {
    return { 
      valid: false, 
      error: `${fieldName} ne peut pas dépasser ${max} caractères` 
    };
  }
  
  return { valid: true };
};

/**
 * Valide un formulaire complet
 * 
 * @example
 * const validations = {
 *   email: () => validateEmail(formData.email),
 *   password: () => validatePassword(formData.password),
 *   phone: () => validatePhone(formData.phone)
 * };
 * 
 * const { valid, errors } = validateForm(validations);
 */
export const validateForm = (validations) => {
  const errors = {};
  let isValid = true;
  
  for (const [field, validateFn] of Object.entries(validations)) {
    const result = validateFn();
    if (!result.valid) {
      errors[field] = result.error;
      isValid = false;
    }
  }
  
  return { valid: isValid, errors };
};

/**
 * Hook React pour validation de formulaire
 * 
 * @example
 * const { errors, validateField, validateAll, clearError } = useFormValidation();
 * 
 * <input
 *   name="email"
 *   onChange={(e) => validateField('email', () => validateEmail(e.target.value))}
 * />
 * {errors.email && <span className="error">{errors.email}</span>}
 */
export const useFormValidation = () => {
  const [errors, setErrors] = React.useState({});
  
  const validateField = (fieldName, validateFn) => {
    const result = validateFn();
    
    if (!result.valid) {
      setErrors(prev => ({ ...prev, [fieldName]: result.error }));
    } else {
      setErrors(prev => {
        const { [fieldName]: _, ...rest } = prev;
        return rest;
      });
    }
    
    return result.valid;
  };
  
  const validateAll = (validations) => {
    const { valid, errors: newErrors } = validateForm(validations);
    setErrors(newErrors);
    return valid;
  };
  
  const clearError = (fieldName) => {
    setErrors(prev => {
      const { [fieldName]: _, ...rest } = prev;
      return rest;
    });
  };
  
  const clearAll = () => {
    setErrors({});
  };
  
  return { errors, validateField, validateAll, clearError, clearAll };
};

// Pour import dans d'autres fichiers
export default {
  validateEmail,
  validatePassword,
  validatePasswordMatch,
  validatePhone,
  validateAmount,
  validateRequired,
  validateURL,
  validateLength,
  validateForm,
  useFormValidation
};
