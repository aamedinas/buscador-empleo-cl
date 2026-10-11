import type { NextAuthOptions } from "next-auth";
import KeycloakProvider from "next-auth/providers/keycloak";

/**
 * buscador-empleo-frontend es un cliente publico de Keycloak
 * (Authorization Code + PKCE, sin client secret). Por eso se fuerza
 * token_endpoint_auth_method "none": Keycloak no espera (ni acepta)
 * un client_secret en el intercambio del codigo por el token para
 * este tipo de cliente.
 */
export const authOptions: NextAuthOptions = {
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_CLIENT_ID ?? "",
      clientSecret: "",
      issuer: process.env.KEYCLOAK_ISSUER,
      checks: ["pkce", "state"],
      client: {
        token_endpoint_auth_method: "none",
      },
    }),
  ],
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, account }) {
      // Solo en el primer login hay `account`; ahi se guarda el
      // access_token de Keycloak para reenviarlo al backend.
      if (account) {
        token.accessToken = account.access_token;
        token.accessTokenExpiresAt = account.expires_at ? account.expires_at * 1000 : undefined;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string | undefined;
      session.accessTokenExpired = token.accessTokenExpiresAt
        ? Date.now() > (token.accessTokenExpiresAt as number)
        : false;
      return session;
    },
  },
  pages: {
    signIn: "/",
  },
};
