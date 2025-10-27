import { useState, useCallback } from 'react';

/**
 * Custom hook for form management
 * 
 * Features:
 * - Form state management
 * - Validation
 * - Error handling
 * - Reset functionality
 * - Dirty state tracking
 * 
 * @param {Object} initialValues - Initial form values
 * @param {Function} validationSchema - Validation function
 * @returns {Object} Form state and methods
 */
export const useForm = (initialValues = {}, validationSchema = null) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDirty, setIsDirty] = useState(false);

  /**
   * Validate single field
   * @param {string} name - Field name
   * @param {any} value - Field value
   * @returns {string|null} Error message
   */
  const validateField = useCallback(
    (name, value) => {
      if (!validationSchema) return null;

      try {
        validationSchema[name]?.(value, values);
        return null;
      } catch (err) {
        return err.message;
      }
    },
    [validationSchema, values]
  );

  /**
   * Validate all fields
   * @returns {Object} Errors object
   */
  const validateForm = useCallback(() => {
    if (!validationSchema) return {};

    const newErrors = {};

    Object.keys(values).forEach((key) => {
      const error = validateField(key, values[key]);
      if (error) {
        newErrors[key] = error;
      }
    });

    return newErrors;
  }, [values, validateField, validationSchema]);

  /**
   * Handle input change
   * @param {Event|Object} e - Event or { name, value }
   */
  const handleChange = useCallback(
    (e) => {
      const { name, value } = e.target || e;

      setValues((prev) => ({
        ...prev,
        [name]: value,
      }));

      setIsDirty(true);

      // Validate field if it has been touched
      if (touched[name]) {
        const error = validateField(name, value);
        setErrors((prev) => ({
          ...prev,
          [name]: error,
        }));
      }
    },
    [touched, validateField]
  );

  /**
   * Handle input blur
   * @param {Event|string} e - Event or field name
   */
  const handleBlur = useCallback(
    (e) => {
      const name = typeof e === 'string' ? e : e.target.name;

      setTouched((prev) => ({
        ...prev,
        [name]: true,
      }));

      // Validate field on blur
      const error = validateField(name, values[name]);
      setErrors((prev) => ({
        ...prev,
        [name]: error,
      }));
    },
    [values, validateField]
  );

  /**
   * Set specific field value
   * @param {string} name - Field name
   * @param {any} value - Field value
   */
  const setFieldValue = useCallback((name, value) => {
    setValues((prev) => ({
      ...prev,
      [name]: value,
    }));
    setIsDirty(true);
  }, []);

  /**
   * Set specific field error
   * @param {string} name - Field name
   * @param {string} error - Error message
   */
  const setFieldError = useCallback((name, error) => {
    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }));
  }, []);

  /**
   * Set field as touched
   * @param {string} name - Field name
   */
  const setFieldTouched = useCallback((name) => {
    setTouched((prev) => ({
      ...prev,
      [name]: true,
    }));
  }, []);

  /**
   * Reset form to initial values
   */
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
    setIsDirty(false);
  }, [initialValues]);

  /**
   * Handle form submission
   * @param {Function} onSubmit - Submit handler
   * @returns {Function} Submit handler
   */
  const handleSubmit = useCallback(
    (onSubmit) => async (e) => {
      if (e && e.preventDefault) {
        e.preventDefault();
      }

      // Validate all fields
      const formErrors = validateForm();
      setErrors(formErrors);

      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce((acc, key) => {
        acc[key] = true;
        return acc;
      }, {});
      setTouched(allTouched);

      // Don't submit if there are errors
      if (Object.keys(formErrors).length > 0) {
        return;
      }

      setIsSubmitting(true);

      try {
        await onSubmit(values);
      } catch (err) {
        console.error('Form submission error:', err);
        
        // Handle validation errors from API
        if (err.response?.data?.errors) {
          setErrors(err.response.data.errors);
        }
      } finally {
        setIsSubmitting(false);
      }
    },
    [values, validateForm]
  );

  /**
   * Check if form is valid
   * @returns {boolean} Is valid
   */
  const isValid = useCallback(() => {
    return Object.keys(validateForm()).length === 0;
  }, [validateForm]);

  /**
   * Get field props for input binding
   * @param {string} name - Field name
   * @returns {Object} Input props
   */
  const getFieldProps = useCallback(
    (name) => ({
      name,
      value: values[name] || '',
      onChange: handleChange,
      onBlur: handleBlur,
    }),
    [values, handleChange, handleBlur]
  );

  return {
    values,
    errors,
    touched,
    isSubmitting,
    isDirty,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
    setFieldTouched,
    resetForm,
    isValid,
    getFieldProps,
  };
};

/**
 * Simple validation schema builder
 * 
 * @example
 * const schema = {
 *   email: validators.required().email(),
 *   password: validators.required().minLength(8),
 *   age: validators.required().min(18).max(100)
 * }
 */
export const validators = {
  required: (message = 'This field is required') => (value) => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      throw new Error(message);
    }
  },

  email: (message = 'Invalid email address') => (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (value && !emailRegex.test(value)) {
      throw new Error(message);
    }
  },

  minLength: (length, message) => (value) => {
    if (value && value.length < length) {
      throw new Error(message || `Must be at least ${length} characters`);
    }
  },

  maxLength: (length, message) => (value) => {
    if (value && value.length > length) {
      throw new Error(message || `Must be at most ${length} characters`);
    }
  },

  min: (min, message) => (value) => {
    if (value && Number(value) < min) {
      throw new Error(message || `Must be at least ${min}`);
    }
  },

  max: (max, message) => (value) => {
    if (value && Number(value) > max) {
      throw new Error(message || `Must be at most ${max}`);
    }
  },

  pattern: (regex, message = 'Invalid format') => (value) => {
    if (value && !regex.test(value)) {
      throw new Error(message);
    }
  },

  match: (fieldName, message) => (value, values) => {
    if (value !== values[fieldName]) {
      throw new Error(message || `Must match ${fieldName}`);
    }
  },

  url: (message = 'Invalid URL') => (value) => {
    try {
      if (value) new URL(value);
    } catch {
      throw new Error(message);
    }
  },
};

export default useForm;
