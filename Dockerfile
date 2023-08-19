FROM ubuntu:jammy
COPY . .

RUN apt-get update && apt-get upgrade -y && apt-get install -y wget unzip python3 python3-pip git
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Stockfish - Depending on your CPU it may be necessary to pick a binary other than bmi2
RUN wget https://abrok.eu/stockfish/latest/linux/stockfish_x64_bmi2.zip -O stockfish.zip
RUN unzip stockfish.zip && rm stockfish.zip
RUN mv stockfish_* ./stockfish && chmod +x ./stockfish

# Fairy-Stockfish - Depending on your CPU it may be necessary to pick a binary other than bmi2
# To use Fairy-Stockfish, uncomment the following lines and adjust config.yml.default accordingly
RUN wget https://github.com/ianfab/Fairy-Stockfish/releases/download/fairy_sf_14_0_1_xq/fairy-stockfish-largeboard_x86-64-bmi2
RUN mv fairy-stockfish-largeboard_x86-64-bmi2 ./fairy-stockfish && chmod +x ./fairy-stockfish
RUN wget "https://drive.google.com/u/0/uc?id=1r5o5jboZRqND8picxuAbA0VXXMJM1HuS&export=download" -O ./3check-313cc226a173.nnue
RUN wget "https://drive.google.com/u/0/uc?id=1SBLSmQmfrsxFHa3ntAhfYXyL3CoVSSL2&export=download" -O ./antichess-689c016df8e0.nnue
RUN wget "https://drive.google.com/u/0/uc?id=1bC7T3iDft8Kbuxlu3Vm2fERxk7cOSoDy&export=download" -O ./atomic-2cf13ff256cc.nnue
RUN wget "https://drive.google.com/u/0/uc?id=1nieguR4yCb0BlME-AUhcrFYkmyIOGvqs&export=download" -O ./crazyhouse-8ebf84784ad2.nnue
RUN wget "https://drive.google.com/u/0/uc?id=16BQztGqFIS1n_dYtmdfFVE2EexF-KagX&export=download" -O ./horde-28173ddccabe.nnue
RUN wget "https://drive.google.com/u/0/uc?id=1x25r_1PgB5XqttkfR494M4rseiIm0BAV&export=download" -O ./kingofthehill-978b86d0e6a4.nnue
RUN wget "https://drive.google.com/u/0/uc?id=1Tiq8FqSu7eiekE2iaWQzSdJPg-mhvLzJ&export=download" -O ./racingkings-636b95f085e3.nnue
RUN wget "https://tests.stockfishchess.org/api/nn/nn-4ffa203f3b58.nnue" -O engines/nn-4ffa203f3b58.nnue

# Add the "--matchmaking" flag to start the matchmaking mode.
CMD python3 user_interface.py
