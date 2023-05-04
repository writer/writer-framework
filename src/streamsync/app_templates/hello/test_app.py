import pandas as pd
import main


class TestApp:

    app_state = main.ss.initial_state

    def test_handle_timer_tick(self):
        main.handle_timer_tick(self.app_state)
        df1 = self.app_state["random_df"].to_dict()
        main.handle_timer_tick(self.app_state)
        df2 = self.app_state["random_df"].to_dict()
        assert df1 != df2

    def test_highlighted_members(self):
        hml = self.app_state["highlighted_members"]
        assert isinstance(hml, list)
        assert len(hml) > 0

    def test_metrics(self):

        data = {
            "weight_g": [3000, 3500, 3200, 3100, 2900, 3300],
            "length_cm": [50, 52, 51, 48, 47, 53],
            "feather_color": ["blue", "blue", "red", "green", "blue", "red"],
        }

        main_df = pd.DataFrame(data)
        self.app_state["main_df"] = main_df

        main._update_metrics(self.app_state)

        assert self.app_state["metrics"]["average_weight"] == 3167
        assert self.app_state["metrics"]["average_length"] == 50
        assert self.app_state["metrics"]["average_bmi"] == 12.6
        assert self.app_state["metrics"]["diversity"] == 0.5

        assert self.app_state["metrics"]["average_weight_note"] == "+Acceptable"
        assert self.app_state["metrics"]["average_length_note"] == "+Acceptable"
        assert self.app_state["metrics"]["average_bmi_note"] == "-Overweight"
        assert self.app_state["metrics"]["diversity_note"] == "-Not diverse"