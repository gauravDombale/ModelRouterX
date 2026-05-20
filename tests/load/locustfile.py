from locust import HttpUser, between, task


class GatewayUser(HttpUser):
    wait_time = between(0.1, 1.0)

    @task
    def chat(self):
        self.client.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer ${MRX_API_KEY}"},
            json={"model": "auto", "messages": [{"role": "user", "content": "Summarize ModelRouterX in one sentence"}]},
        )

