from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, f1_score, accuracy_score
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def gerar_matriz_confusão(pred_col, verdadeiro_col, csv_file):

    df = pd.read_csv(csv_file)

    y_pred = df[pred_col]
    y_verdadeiro = df[verdadeiro_col]

    cm = confusion_matrix(y_verdadeiro, y_pred, labels=['Positive', 'Negative', 'Neutral'])

    cm_display = ConfusionMatrixDisplay(confusion_matrix = cm, display_labels = ['Positive', 'Negative', 'Neutral'])
    
    acuracia = accuracy_score(y_verdadeiro, y_pred)
    f1 = f1_score(y_verdadeiro, y_pred, average='weighted')
    print({'Acurácia': acuracia, 'F1 Score': f1})
    cm_display.plot()
    plt.show()

gerar_matriz_confusão('sentimento_modelo', 'sentimento_esperado', 'fan-voice-llm-project/Analise_Torcedor.csv')