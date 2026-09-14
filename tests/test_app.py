import io
import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import soundfile as sf

from app import app
from backend import app as backend_app
from frontend import app as frontend_app
from config import MAX_CONTENT_LENGTH, MAX_AUDIO_DURATION_SECONDS, MAX_HISTORY_ITEMS
from separator_core.audio_utils import validate_audio_file, get_audio_info
from separator_core.history_manager import get_history, add_history_entry, delete_history_entry, clear_history
from separator_core.model_manager import get_models_list

class TestAIMusicSeparator(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        for fname in ["debug_test.py", "test_load.py", "temp_test.wav"]:
            p = Path(__file__).resolve().parent.parent / fname
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        self.client = app.test_client()
        self.test_dir = Path("data/test_tmp")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        clear_history()

    def tearDown(self):
        clear_history()
        # Clean up test files
        for f in self.test_dir.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
        try:
            self.test_dir.rmdir()
        except Exception:
            pass

    def test_system_info_api(self):
        res = self.client.get("/api/system_info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("cuda_available"))
        self.assertIn("NVIDIA", data.get("device_name"))

    def test_models_list_api(self):
        res = self.client.get("/api/models")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        models = data.get("models")
        self.assertGreater(len(models), 0)
        model_ids = [m["id"] for m in models]
        self.assertIn("mel_band_roformer_kim_ft3_unwa.ckpt", model_ids)
        self.assertIn("UVR-MDX-NET-Inst_HQ_3.onnx", model_ids)

    def test_settings_api(self):
        res = self.client.get("/api/settings")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        
        # Test update
        post_res = self.client.post("/api/settings", json={"theme": "light", "output_format": "MP3"})
        self.assertEqual(post_res.status_code, 200)
        updated = post_res.get_json().get("settings")
        self.assertEqual(updated.get("theme"), "light")
        self.assertEqual(updated.get("output_format"), "MP3")

    def test_history_max_67_items(self):
        # Insert 75 items
        for i in range(75):
            add_history_entry({
                "file_id": f"test_file_{i}",
                "original_filename": f"song_{i}.mp3",
                "model_used": "mel_band_roformer_kim_ft3_unwa.ckpt",
                "device_used": "cuda",
                "processing_time": "12s",
                "stems": []
            })
        history = get_history()
        # Requirement: Max is 67
        self.assertEqual(len(history), 67)
        # Verify FIFO: most recent item (song_74) is first
        self.assertEqual(history[0]["original_filename"], "song_74.mp3")
        # Oldest items (0 through 7) must have been dropped
        self.assertEqual(history[-1]["original_filename"], "song_8.mp3")

    def test_audio_duration_validation(self):
        # Create a valid 3-second audio file
        sr = 22050
        duration_short = 3.0
        y_short = np.sin(2 * np.pi * 440 * np.linspace(0, duration_short, int(sr * duration_short)))
        short_file = self.test_dir / "valid_short.wav"
        sf.write(str(short_file), y_short, sr)

        is_valid, msg, meta = validate_audio_file(short_file)
        self.assertTrue(is_valid)
        self.assertEqual(meta["duration_seconds"], 3.0)

        # Create a test audio file exceeding 8 minutes (e.g. 500 seconds = 8m20s)
        # To avoid huge memory, write silence with low sample rate or dummy wav header
        sr_low = 8000
        duration_long = 500.0  # > 480 seconds (8 minutes)
        y_long = np.zeros(int(sr_low * duration_long), dtype=np.float32)
        long_file = self.test_dir / "overlong.wav"
        sf.write(str(long_file), y_long, sr_low)

        is_valid, msg, meta = validate_audio_file(long_file)
        self.assertFalse(is_valid)
        self.assertIn("vượt quá giới hạn cho phép (8 phút", msg)

    def test_upload_api_with_valid_and_invalid_audio(self):
        # 1. Valid short audio
        sr = 16000
        duration = 2.0
        y = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))
        wav_io = io.BytesIO()
        sf.write(wav_io, y, sr, format="WAV")
        wav_io.seek(0)

        res = self.client.post("/api/upload", data={"audio_file": (wav_io, "test_track.wav")})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("original_filename"), "test_track.wav")
        self.assertEqual(data["metadata"]["duration_seconds"], 2.0)

        # 2. Overlong audio (> 8 minutes)
        sr_low = 4000
        duration_long = 490.0  # > 480 seconds
        y_long = np.zeros(int(sr_low * duration_long), dtype=np.float32)
        wav_long_io = io.BytesIO()
        sf.write(wav_long_io, y_long, sr_low, format="WAV")
        wav_long_io.seek(0)

        res_long = self.client.post("/api/upload", data={"audio_file": (wav_long_io, "long_track.wav")})
        self.assertEqual(res_long.status_code, 400)
        data_long = res_long.get_json()
        self.assertFalse(data_long.get("success"))
        self.assertIn("vượt quá giới hạn cho phép (8 phút", data_long.get("error", ""))

    def test_backend_health_and_cors(self):
        backend_client = backend_app.test_client()
        res = backend_client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("AI Music Source Separation", data.get("service"))
        # Verify CORS headers
        self.assertEqual(res.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("GET", res.headers.get("Access-Control-Allow-Methods"))

    def test_backend_preflight_options(self):
        backend_client = backend_app.test_client()
        res = backend_client.open("/api/upload", method="OPTIONS")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(res.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("POST", res.headers.get("Access-Control-Allow-Methods"))

    def test_frontend_routes(self):
        front_client = frontend_app.test_client()
        
        # Test health
        health_res = front_client.get("/health")
        self.assertEqual(health_res.status_code, 200)
        self.assertEqual(health_res.get_json().get("status"), "online")

        # Test index page rendering
        index_res = front_client.get("/")
        self.assertEqual(index_res.status_code, 200)
        html = index_res.get_data(as_text=True)
        self.assertIn("AI Music Source Separation", html)
        self.assertIn("window.BACKEND_API_URL", html)
        self.assertIn("UI :3000", html)
        self.assertIn("API :5000", html)

    def test_numba_cache_configuration(self):
        from config import NUMBA_CACHE_DIR
        self.assertTrue(NUMBA_CACHE_DIR.exists())
        self.assertEqual(os.environ.get("NUMBA_CACHE_DIR"), str(NUMBA_CACHE_DIR))
        # Ensure directory is writable
        test_probe = NUMBA_CACHE_DIR / ".write_test"
        try:
            test_probe.write_text("ok", encoding="utf-8")
            self.assertTrue(test_probe.exists())
        finally:
            if test_probe.exists():
                test_probe.unlink()

if __name__ == "__main__":
    unittest.main()














