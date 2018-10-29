import importlib.util;
spec = importlib.util.spec_from_file_location("jpeg", "../python/jpeg.py");
jpeg = importlib.util.module_from_spec(spec);
spec.loader.exec_module(jpeg);
