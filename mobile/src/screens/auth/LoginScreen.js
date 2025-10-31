/**
 * Login Screen
 * User authentication screen
 */

import React, {useState} from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Image,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Title,
  Headline,
  HelperText,
} from 'react-native-paper';
import {useAuth} from '../../contexts/AuthContext';
import {useToast} from '../../contexts/ToastContext';
import theme, {spacing} from '../../utils/theme';

const LoginScreen = ({navigation}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {login} = useAuth();
  const toast = useToast();

  const handleLogin = async () => {
    if (!email || !password) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }

    setLoading(true);
    const result = await login(email, password);
    setLoading(false);

    if (result.success) {
      toast.success('Connexion réussie !');
    } else {
      toast.error(result.error || 'Erreur de connexion');
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled">
        <View style={styles.logoContainer}>
          <Headline style={styles.logo}>ShareYourSales</Headline>
          <Text style={styles.subtitle}>
            Plateforme d'Affiliation entre Influenceurs et Marchands
          </Text>
        </View>

        <View style={styles.formContainer}>
          <Title style={styles.title}>Connexion</Title>

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            left={<TextInput.Icon icon="email" />}
            style={styles.input}
          />

          <TextInput
            label="Mot de passe"
            value={password}
            onChangeText={setPassword}
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

          <Button
            mode="text"
            onPress={() => navigation.navigate('ForgotPassword')}
            style={styles.forgotButton}>
            Mot de passe oublié ?
          </Button>

          <Button
            mode="contained"
            onPress={handleLogin}
            loading={loading}
            disabled={loading}
            style={styles.loginButton}>
            Se Connecter
          </Button>

          <View style={styles.registerContainer}>
            <Text style={styles.registerText}>Pas encore de compte ?</Text>
            <Button
              mode="text"
              onPress={() => navigation.navigate('Register')}
              compact>
              S'inscrire
            </Button>
          </View>

          <View style={styles.demoContainer}>
            <Text style={styles.demoTitle}>Comptes de démonstration :</Text>
            <Text style={styles.demoText}>
              📱 Influenceur: influencer@example.com / pass123
            </Text>
            <Text style={styles.demoText}>
              🏪 Marchand: merchant@example.com / pass123
            </Text>
            <Text style={styles.demoText}>
              👤 Admin: admin@tracknow.io / admin123
            </Text>
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
  logoContainer: {
    alignItems: 'center',
    marginTop: spacing.xxl,
    marginBottom: spacing.xl,
  },
  logo: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  formContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 16,
    padding: spacing.lg,
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
  input: {
    marginBottom: spacing.md,
  },
  forgotButton: {
    alignSelf: 'flex-end',
    marginBottom: spacing.md,
  },
  loginButton: {
    marginTop: spacing.md,
    paddingVertical: spacing.xs,
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  registerText: {
    color: theme.colors.textSecondary,
  },
  demoContainer: {
    marginTop: spacing.xl,
    padding: spacing.md,
    backgroundColor: theme.colors.background,
    borderRadius: 8,
  },
  demoTitle: {
    fontWeight: 'bold',
    marginBottom: spacing.sm,
    color: theme.colors.text,
  },
  demoText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginBottom: spacing.xs,
  },
});

export default LoginScreen;
