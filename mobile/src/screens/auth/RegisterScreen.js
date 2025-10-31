/**
 * Register Screen
 * User registration screen
 */

import React, {useState} from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Title,
  RadioButton,
  HelperText,
} from 'react-native-paper';
import {useAuth} from '../../contexts/AuthContext';
import {useToast} from '../../contexts/ToastContext';
import theme, {spacing} from '../../utils/theme';

const RegisterScreen = ({navigation}) => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    role: 'influencer', // influencer, merchant
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {register} = useAuth();
  const toast = useToast();

  const handleRegister = async () => {
    // Validation
    if (!formData.fullName || !formData.email || !formData.password) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setLoading(true);
    const result = await register({
      full_name: formData.fullName,
      email: formData.email,
      password: formData.password,
      phone: formData.phone,
      role: formData.role,
    });
    setLoading(false);

    if (result.success) {
      toast.success('Inscription réussie ! Veuillez vous connecter.');
      navigation.navigate('Login');
    } else {
      toast.error(result.error || 'Erreur d\'inscription');
    }
  };

  const updateFormData = (field, value) => {
    setFormData(prev => ({...prev, [field]: value}));
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled">
        <View style={styles.formContainer}>
          <Title style={styles.title}>Créer un compte</Title>

          <Text style={styles.label}>Type de compte *</Text>
          <RadioButton.Group
            onValueChange={value => updateFormData('role', value)}
            value={formData.role}>
            <View style={styles.radioContainer}>
              <View style={styles.radioItem}>
                <RadioButton value="influencer" />
                <Text>Influenceur</Text>
              </View>
              <View style={styles.radioItem}>
                <RadioButton value="merchant" />
                <Text>Marchand</Text>
              </View>
            </View>
          </RadioButton.Group>

          <TextInput
            label="Nom complet *"
            value={formData.fullName}
            onChangeText={value => updateFormData('fullName', value)}
            mode="outlined"
            left={<TextInput.Icon icon="account" />}
            style={styles.input}
          />

          <TextInput
            label="Email *"
            value={formData.email}
            onChangeText={value => updateFormData('email', value)}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            left={<TextInput.Icon icon="email" />}
            style={styles.input}
          />

          <TextInput
            label="Téléphone"
            value={formData.phone}
            onChangeText={value => updateFormData('phone', value)}
            mode="outlined"
            keyboardType="phone-pad"
            left={<TextInput.Icon icon="phone" />}
            style={styles.input}
          />

          <TextInput
            label="Mot de passe *"
            value={formData.password}
            onChangeText={value => updateFormData('password', value)}
            mode="outlined"
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            left={<TextInput.Icon icon="lock" />}
            right={
              <TextInput.Icon
                icon={showPassword ? 'eye-off' : 'eye'}
                onPress={() => setShowPassword(!showPassword)}
              />
            }
            style={styles.input}
          />

          <TextInput
            label="Confirmer le mot de passe *"
            value={formData.confirmPassword}
            onChangeText={value => updateFormData('confirmPassword', value)}
            mode="outlined"
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            left={<TextInput.Icon icon="lock-check" />}
            style={styles.input}
          />

          <HelperText type="info" visible={true}>
            Le mot de passe doit contenir au moins 6 caractères
          </HelperText>

          <Button
            mode="contained"
            onPress={handleRegister}
            loading={loading}
            disabled={loading}
            style={styles.registerButton}>
            S'inscrire
          </Button>

          <View style={styles.loginContainer}>
            <Text style={styles.loginText}>Déjà un compte ?</Text>
            <Button
              mode="text"
              onPress={() => navigation.navigate('Login')}
              compact>
              Se connecter
            </Button>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    padding: spacing.lg,
  },
  formContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 16,
    padding: spacing.lg,
    marginTop: spacing.xl,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: spacing.lg,
    color: theme.colors.text,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: spacing.sm,
    color: theme.colors.text,
  },
  radioContainer: {
    flexDirection: 'row',
    marginBottom: spacing.lg,
  },
  radioItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: spacing.xl,
  },
  input: {
    marginBottom: spacing.md,
  },
  registerButton: {
    marginTop: spacing.md,
    paddingVertical: spacing.xs,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  loginText: {
    color: theme.colors.textSecondary,
  },
});

export default RegisterScreen;
