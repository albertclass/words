package services

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"golang.org/x/oauth2"
)

var (
	cliId       = "zixel"
	cliSecret   = "zixel"
	deamon      = "http://localhost:8080"
	redirectURL = "/callback"
)

var cfg = &oauth2.Config{
	ClientID:     cliId,
	ClientSecret: cliSecret,
	RedirectURL:  deamon + redirectURL,
	Scopes:       []string{"openid", "profile", "email"},
	Endpoint: oauth2.Endpoint{
		AuthURL:  deamon + "/authorize",
		TokenURL: deamon + "/token",
	},
}

func handleRedirect(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, oauth2Config.AuthCodeURL(state), http.StatusFound)
}

func handleRedirect(c *gin.Context) {
	c.Redirect(http.StatusFound, cfg.AuthCodeURL("state"))
}

func callbackHandler(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		c.String(http.StatusBadRequest, "%s", "Missing authorization code")
		return
	}

	token, err := cfg.Exchange(c, code)
	if err != nil {
		c.String(http.StatusBadRequest, "%s", err.Error())
		return
	}

	c.SetCookie("access_token", token.AccessToken, 3600, "/", "localhost", false, true)
	c.Redirect(http.StatusFound, "/")
}
