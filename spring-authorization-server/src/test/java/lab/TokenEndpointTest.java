package lab;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class TokenEndpointTest {
    @Autowired MockMvc mvc;

    @Test
    void clientCredentialsIssuesBearerToken() throws Exception {
        mvc.perform(post("/oauth2/token").with(httpBasic("orders-service", "lab-secret"))
                .param("grant_type", "client_credentials").param("scope", "orders.read"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.token_type").value("Bearer"))
            .andExpect(jsonPath("$.access_token").isNotEmpty());
    }

    @Test
    void badSecretIs401() throws Exception {
        mvc.perform(post("/oauth2/token").with(httpBasic("orders-service", "wrong"))
                .param("grant_type", "client_credentials"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void discoveryAndJwksArePublished() throws Exception {
        mvc.perform(get("/.well-known/openid-configuration")).andExpect(status().isOk())
            .andExpect(jsonPath("$.issuer").value("http://localhost:9000"));
        mvc.perform(get("/oauth2/jwks")).andExpect(status().isOk());
    }
}
