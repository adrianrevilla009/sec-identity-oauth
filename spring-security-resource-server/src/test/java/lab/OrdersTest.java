package lab;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class OrdersTest {
    @Autowired MockMvc mvc;

    @Test
    void noTokenIs401() throws Exception {
        mvc.perform(get("/orders")).andExpect(status().isUnauthorized());
    }

    @Test
    void readScopeCanList() throws Exception {
        mvc.perform(get("/orders").with(jwt().authorities(new SimpleGrantedAuthority("SCOPE_orders.read"))))
            .andExpect(status().isOk());
    }

    @Test
    void wrongScopeIs403() throws Exception {
        mvc.perform(get("/orders").with(jwt().authorities(new SimpleGrantedAuthority("SCOPE_other"))))
            .andExpect(status().isForbidden());
    }

    @Test
    void writeNeedsWriteScopeViaMethodSecurity() throws Exception {
        mvc.perform(post("/orders").with(jwt().authorities(new SimpleGrantedAuthority("SCOPE_orders.read"))))
            .andExpect(status().isForbidden());
        mvc.perform(post("/orders").with(jwt().authorities(new SimpleGrantedAuthority("SCOPE_orders.write"))))
            .andExpect(status().isOk());
    }
}
