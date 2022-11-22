import setuptools

setuptools.setup(
    name="photo-organizer",
    description="A quick and dirty script/application designed to allow my wife to quickly pre-process 10s of gigabytes of photos she found on some old hard drives. These drives had different organization patterns and many drives contained duplicates.",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "altgraph==0.17",
        "ImageHash==4.1.0",
        "macholib==1.14",
        "numpy==1.21.0",
        "Pillow==9.3.0",
        "PyInstaller==3.6",
        "PyWavelets==1.1.1",
        "scipy==1.4.1",
        "six==1.15.0"
    ],
    extras_require={
        "dev": [
            "autopep8==1.5.3",
            "flake8==3.8.1"
        ]
    }
)
