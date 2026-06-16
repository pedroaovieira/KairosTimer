# Keep ViewBinding classes
-keep class org.pedrov.kairostimer.databinding.** { *; }

# Keep data classes used with JSON (PhasesRepository / Gson)
-keep class org.pedrov.kairostimer.PhaseConfig { *; }

# Standard Android keep rules (covered by proguard-android-optimize.txt, listed for clarity)
-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable
