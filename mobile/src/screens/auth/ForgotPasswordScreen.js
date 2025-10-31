/**
 * Forgot Password Screen
 */

import React, {useState} from 'react';
import {View, StyleSheet, ScrollView} from 'react-native';
import {TextInput, Button, Text, Title} from 'react-native-paper';
import {useToast} from '../../contexts/ToastContext';
import theme, {spacing} from '../../utils/theme';

const ForgotPasswordScreen = ({navigation}) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleResetPassword = async () => {
    if (!email) {
      toast.error('Veuillez entrer votre email');
      return;
    }

    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      toast.success('Email de réinitialisation envoyé !');
      navigation.navigate('Login');
    }, 1500);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.formContainer}>
        <Title style={styles.title}>Mot de passe oublié</Title>
        <Text style={styles.subtitle}>
          Entrez votre email pour recevoir un lien de réinitialisation
        </Text>

        <TextInput
          label="Email"
          value={email}
          onChangeText={setEmail}
          mode="outlined"
          keyboardType="email-address"
          autoCapitalize="none"
          left={<TextInput.Icon icon="email" />}
          style={styles.input}
        />

        <Button
          mode="contained"
          onPress={handleResetPassword}
          loading={loading}
          disabled={loading}
          style={styles.button}>
          Envoyer
        </Button>

        <Button mode="text" onPress={() => navigation.navigate('Login')}>
          Retour à la connexion
        </Button>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    flexGrow: 1,
    padding: spacing.lg,
    justifyContent: 'center',
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
    marginBottom: spacing.md,
  },
  subtitle: {
    color: theme.colors.textSecondary,
    marginBottom: spacing.lg,
  },
  input: {
    marginBottom: spacing.lg,
  },
  button: {
    marginBottom: spacing.md,
    paddingVertical: spacing.xs,
  },
});

export default ForgotPasswordScreen;
