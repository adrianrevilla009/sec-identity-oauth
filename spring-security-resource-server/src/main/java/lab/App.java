package lab;

import java.util.List;
import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpMethod;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

/** Orders resource server: JWT validated against the issuer, scopes map to SCOPE_* authorities. */
@SpringBootApplication
@EnableMethodSecurity
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }

    @Bean
    SecurityFilterChain chain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(a -> a
                .requestMatchers(HttpMethod.GET, "/orders/**").hasAuthority("SCOPE_orders.read")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(j -> { }))
            .build();
    }

    @RestController
    static class Orders {
        @GetMapping("/orders")
        Map<String, Object> list(@AuthenticationPrincipal Jwt jwt) {
            return Map.of("subject", jwt.getSubject(), "orders", List.of("o-1", "o-2"));
        }

        /** Method security: a finer-grained check on top of the URL rule. */
        @PostMapping("/orders")
        @PreAuthorize("hasAuthority('SCOPE_orders.write')")
        Map<String, String> create() {
            return Map.of("id", "o-3");
        }
    }
}
