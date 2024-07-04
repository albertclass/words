package services

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/coreos/go-oidc"
	"github.com/gin-gonic/gin"
	"golang.org/x/oauth2"
)

var provider *oidc.Provider

func OAuth2Config(cliId, cliSecret, redirectURL string) *oauth2.Config {
	var err error
	provider, err = oidc.NewProvider(context.Background(), "http://localhost:8080")
	if err != nil {
		log.Fatalf("Failed to create provider: %v", err)
	}

	// Configure an OpenID Connect aware OAuth2 client.
	oauth2Config := oauth2.Config{
		ClientID:     cliId,
		ClientSecret: cliSecret,
		RedirectURL:  redirectURL,

		// Discovery returns the OAuth2 endpoints.
		Endpoint: provider.Endpoint(),

		// "openid" is a required scope for OpenID Connect flows.
		Scopes: []string{oidc.ScopeOpenID, "profile", "email"},
	}

	return &oauth2Config
}

func verifyJWT(accessToken string) (*oidc.IDTokenClaims, error) {
	idToken, err := provider.Verifier(&oidc.Config{ClientID: "client_id"}).Verify(context.Background(), accessToken)
	if err != nil {
		return nil, err
	}

	var claims oidc.IDTokenClaims
	if err := idToken.Claims(&claims); err != nil {
		return nil, err
	}

	return &claims, nil
}

func userHandler(c *gin.Context) {
	accessToken := c.Query("access_token")
	if accessToken == "" {
		c.String(http.StatusBadRequest, "Missing access token")
		return
	}

	claims, err := verifyJWT(accessToken)
	if err != nil {
		c.String(http.StatusBadRequest, "%s", err.Error())
		return
	}

	c.String(http.StatusOK, fmt.Sprintf("Hello, %s!", claims.Subject))
}
