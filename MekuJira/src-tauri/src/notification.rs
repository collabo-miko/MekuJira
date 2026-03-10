use std::time::Duration;

use chrono::Datelike;
use tauri::Manager;
use tauri_plugin_notification::NotificationExt;

use crate::store;
use crate::store::config::Weekday;

/// 通知スケジューラーを開始（毎分チェック）
pub fn start(app: tauri::AppHandle) {
    tauri::async_runtime::spawn(async move {
        notification_loop(app).await;
    });
}

async fn notification_loop(app: tauri::AppHandle) {
    loop {
        tokio::time::sleep(Duration::from_secs(60)).await;

        let app_data_dir = match app.path().app_data_dir() {
            Ok(dir) => dir,
            Err(_) => continue,
        };

        let config = match store::config::load(&app_data_dir) {
            Ok(c) => c,
            Err(_) => continue,
        };

        let now = chrono::Local::now();
        let current_time = now.format("%H:%M").to_string();
        let current_day = chrono_to_weekday(now.weekday());

        for schedule in &config.notification_schedules {
            if schedule.enabled
                && schedule.time == current_time
                && schedule.days.contains(&current_day)
            {
                let _ = app
                    .notification()
                    .builder()
                    .title("MekuJira")
                    .body(&schedule.message)
                    .show();
            }
        }
    }
}

fn chrono_to_weekday(day: chrono::Weekday) -> Weekday {
    match day {
        chrono::Weekday::Mon => Weekday::Mon,
        chrono::Weekday::Tue => Weekday::Tue,
        chrono::Weekday::Wed => Weekday::Wed,
        chrono::Weekday::Thu => Weekday::Thu,
        chrono::Weekday::Fri => Weekday::Fri,
        chrono::Weekday::Sat => Weekday::Sat,
        chrono::Weekday::Sun => Weekday::Sun,
    }
}
