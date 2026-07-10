"""Teste rápido do motor DOCX: gera uma apostila completa com conteúdo de demonstração."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ebe.docx.builder import (
    ApostilaConteudo, DocumentBuilder, ExerciciosBloco, GlossarioEntrada, Secao,
)


def build_demo() -> ApostilaConteudo:
    secoes = [
        Secao(
            titulo="O estado de perdição descrito nas Escrituras",
            numero="2.1",
            paragrafos=[
                "A Bíblia é cristalina ao descrever a condição do ser humano fora de Cristo. "
                "Desde a queda de Adão, a humanidade encontra-se sob o domínio do pecado, "
                "incapaz de, por seus próprios esforços, reconciliar-se com Deus.",
                "O apóstolo Paulo, em Romanos 3, reúne uma série de textos do Antigo "
                "Testamento para demonstrar que «não há justo, nem sequer um» (Rm 3.10). "
                "Esta afirmação não é um exagero retórico, mas uma diagnóstico divino da "
                "condição humana.",
            ],
            citacoes=[
                ("Porque todos pecaram e destituídos estão da glória de Deus.", "Romanos 3.23"),
                ("O salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus, nosso Senhor.", "Romanos 6.23"),
            ],
            caixas=[("Para reter", "A perdição não é essencialmente um lugar, mas um estado de separação de Deus que começa já aqui e se consuma na eternidade.")],
        ),
        Secao(
            titulo="As consequências da Queda",
            numero="2.2",
            paragrafos=[
                "Em Génesis 3, vemos que a desobediência de Adão e Eva não ficou sem consequências. "
                "A relação vertical com Deus foi rompida; a relação horizontal entre o homem e a "
                "mulher foi marcada pela vergonha e pela acusação mútua; a relação com a criação "
                "foi ferida pelo suor, pela dor e pela morte.",
                "Estas consequências são universais: «Como por um só homem entrou o pecado no "
                "mundo, e pelo pecado a morte, assim a morte passou a todos os homens, porque "
                "todos pecaram» (Rm 5.12). Não existe excepção cultural, geográfica ou moral.",
            ],
            lista_ordenada=[
                "Morte espiritual — separação imediata de Deus (Gn 2.17, Ef 2.1).",
                "Morte física — deterioração do corpo e retorno ao pó (Gn 3.19, Rm 5.12).",
                "Morte eterna — separação eterna da presença de Deus, chamada «segunda morte» (Ap 20.14).",
            ],
            tabelas=[
                (["Tipo de morte", "Em que consiste", "Referência"],
                 [
                    ["Espiritual", "Separação de Deus no presente", "Efésios 2.1"],
                    ["Física", "Separação da alma e do corpo", "Hebreus 9.27"],
                    ["Eterna", "Separação definitiva no juízo final", "Apocalipse 20.14-15"],
                 ]),
            ],
        ),
        Secao(
            titulo="A total incapacidade humana",
            numero="2.3",
            paragrafos=[
                "Um dos erros mais frequentes no ensino cristão superficial é imaginar que o ser "
                "humano, ainda que ferido pelo pecado, conserva alguma capacidade autónoma para "
                "escolher Deus e fazer o bem à Sua vista. As Escrituras negam isto de forma clara.",
                "Jeremias 17.9 afirma que «enganoso é o coração, mais do que todas as coisas, "
                "e corrupto; quem o conhecerá?» Jesus, por seu turno, ensina que «ninguém pode vir "
                "a mim se o Pai, que me enviou, não o trouxer» (Jo 6.44).",
            ],
            citacoes=[
                ("Não há quem entenda, não há quem busque a Deus. Todos se extraviaram, "
                 "e juntamente se fizeram inúteis; não há quem faça o bem, não há nem um sequer.",
                 "Romanos 3.11-12"),
            ],
        ),
        Secao(
            titulo="Equívocos comuns",
            numero="2.4",
            paragrafos=[
                "É importante compreender correctamente a doutrina do estado de perdição para "
                "não cair nem em extremos laxistas («todo mundo vai para o céu») nem em "
                "posições que minimizem a gravidade do pecado.",
            ],
            subsecoes=[
                Secao(
                    titulo="Equívoco 1 — «No fundo, sou bom.»",
                    paragrafos=["Jesus declarou que «ninguém há bom, senão um, que é Deus» (Mc 10.18). A bondade relativa das pessoas não anula o diagnóstico bíblico; apenas demonstra a graça comum de Deus sobre a humanidade."],
                ),
                Secao(
                    titulo="Equívoco 2 — «Deus é amor, por isso ninguém se perde.»",
                    paragrafos=["Deus é amor, mas é também santo e justo. O próprio Jesus falou mais vezes do inferno do que do céu nos Evangelhos (cf. Mt 10.28, 25.46). A cruz é precisamente a demonstração de que o perdão não barateia a justiça."],
                ),
            ],
            caixas=[("Para reter", "Reconhecer a profundidade do estado de perdição é o primeiro passo para valorizar devidamente a grandeza da salvação em Cristo.")],
        ),
        Secao(
            titulo="A dignidade humana e a severidade do diagnóstico",
            numero="2.5",
            paragrafos=[
                "Falar do estado de perdição não é negar a dignidade do ser humano. Pelo "
                "contrário: o homem e a mulher foram criados à imagem e semelhança de Deus "
                "(Gn 1.27), e por isso a sua queda é trágica precisamente porque cai de uma "
                "posição elevada.",
                "A Bíblia combina realismo e esperança: descreve a humanidade como caída, mas "
                "sem nunca a reduzir a «coisa nenhuma». É precisamente por sermos imagem de "
                "Deus que a salvação tem a forma de redenção e não de substituição.",
            ],
        ),
    ]

    return ApostilaConteudo(
        id_num=1,
        numero="0001",
        titulo="O Estado de Perdição do Ser Humano",
        subtitulo="A condição humana sob o pecado e a necessidade da graça",
        codigo="EBE-APO-0001",
        instituto="Instituto de Formação Cristã",
        escola="Fundamentos da Fé",
        curso="Salvação e Novo Nascimento",
        modulo="Módulo 1 — Fundamentos da Salvação",
        carga_horaria="25 h",
        nivel_formativo="Nível 1 — Discípulo (Conhecer)",
        autor="Direcção Pedagógica · Escola Bíblica Epignósis",
        edicao_ano="1.ª edição — 2026",
        apresentacao=[
            "Esta apostila inaugura o Curso «Salvação e Novo Nascimento» da Escola de "
            "Fundamentos da Fé, no Instituto de Formação Cristã. Ela coloca o fundamento "
            "bíblico sobre o qual todas as demais apostilas serão construídas: a realidade "
            "do pecado e do estado de perdição do ser humano.",
            "Sem uma compreensão clara da nossa condição fora de Cristo, a graça torna-se "
            "uma palavra bonita mas barata; a cruz perde o seu peso; a salvação reduz-se a "
            "autoajuda religiosa. Por isso, antes de estudarmos a obra de Cristo, o novo "
            "nascimento e a vida cristã, precisamos de olhar com sinceridade para o diagnóstico "
            "bíblico da humanidade.",
            "Ao longo destas páginas, examinaremos os textos-chave, refletiremos sobre as "
            "consequências da queda e desfazeremos equívocos comuns. O objectivo não é "
            "produzir culpa, mas conduzir à gratidão: só quem reconhece a profundidade do "
            "abismo pode maravilhar-se verdadeiramente com a mão que o ergue.",
        ],
        objectivos=[
            "CONHECER — definir e explicar, com base bíblica, o que é o estado de perdição do ser humano, identificando as suas três dimensões (espiritual, física e eterna).",
            "CRER — interiorizar a convicção de que «todos pecaram» e que ninguém pode salvar-se a si mesmo, glorificando a Deus pela iniciativa soberana da graça.",
            "VIVER — reconhecer diante de Deus a sua própria incapacidade, abandonando qualquer confiança nas obras ou na bondade própria como meio de salvação.",
            "SERVIR — explicar com clareza, mansidão e fidelidade bíblica a doutrina do pecado e da perdição a outros, recusando tanto o moralismo como o laxismo.",
        ],
        versiculo_chave=(
            "Porque todos pecaram e destituídos estão da glória de Deus.",
            "Romanos 3.23",
        ),
        texto_base="Romanos 1.18–3.20; Génesis 3; Efésios 2.1-10",
        introducao=[
            "Há, no nosso tempo, uma enorme resistência em falar do pecado, da culpa e da "
            "perdição. Proclamamos que «Deus é amor» e esquecemos, com frequência, que o amor "
            "santo de Deus não negocia com o mal. O resultado é um evangelho encurtado, que "
            "promete bênçãos sem exigir arrependimento e céu sem cruz.",
            "Mas os apóstolos não pregaram assim. Quando o apóstolo Paulo escreve a sua epístola "
            "aos Romanos, ele não começa pela graça: começa pelo diagnóstico. Os capítulos "
            "iniciais (Rm 1–3) constroem, passo a passo, a acusação divina contra toda a "
            "humanidade — judeus e gentios igualmente. Só depois de fechar «todos debaixo de "
            "pecado» (Rm 11.32) é que ele revela a maravilha da justificação pela fé.",
            "Nesta apostila seguiremos o mesmo caminho. Olharemos honestamente para o que a "
            "Escritura diz sobre o nosso estado natural, a fim de que, na próxima apostila, "
            "possamos contemplar, com a devida admiração, a graça de Deus em Cristo.",
        ],
        secoes_desenvolvimento=secoes,
        aplicacao_pratica=[
            "A doutrina do estado de perdição não é um exercício académico estéril. Ela deve "
            "transformar a forma como vivemos, oramos, adoramos e testemunhamos.",
        ],
        aplicacao_itens=[
            "Na vida devocional — reserve tempo nesta semana para ler Romanos 1–3 numa só leitura. Peça ao Espírito Santo que lhe mostre a verdade sobre si mesmo e sobre a cruz.",
            "Na família — converse com os seus filhos ou cônjuge sobre Génesis 3, explicando, em linguagem simples, por que o mundo está quebrantado e por que precisamos de um Salvador.",
            "Na igreja local — ao ensinar ou partilhar, não minimize o pecado para «não ofender». A verdade que liberta começa por ser a verdade que expõe (Jo 8.32).",
            "No testemunho — quando anunciar o Evangelho, apresente primeiro a diagnose bíblica (pecado, culpa, juízo) e só depois o remédio em Cristo. Um evangelho sem lei produz conversões rasas.",
            "Na adoração — deixe que a consciência da sua condição de salvo pela graça aumente a sua gratidão. Quem mais foi perdoado, mais ama (Lc 7.47).",
        ],
        sintese=[
            "Nesta apostila vimos que o ser humano, fora de Cristo, está sob o domínio do "
            "pecado e em estado de perdição. Esta condição é universal (todos pecaram), "
            "profunda (atinge mente, coração e vontade) e grave (implica separação de Deus "
            "no tempo e na eternidade).",
            "Longe de ser um convite ao desespero, este diagnóstico é a porta para a esperança: "
            "quando reconhecemos que não podemos salvar-nos a nós mesmos, estamos finalmente "
            "prontos para olhar para Aquele que veio buscar e salvar o que se havia perdido "
            "(Lc 19.10).",
        ],
        exercicios=[
            ExerciciosBloco(
                titulo="I — Verifique a sua compreensão",
                itens=[
                    "Em suas próprias palavras, defina o que a Bíblia entende por «estado de perdição».",
                    "Explique as três dimensões da morte resultantes da queda (espiritual, física e eterna).",
                    "Que argumentos o apóstolo Paulo usa em Romanos 1–3 para demonstrar que judeus e gentios estão debaixo do pecado?",
                    "O que significa dizer que o ser humano é moralmente incapaz de salvar-se a si mesmo?",
                ],
            ),
            ExerciciosBloco(
                titulo="II — Reflexão pessoal",
                itens=[
                    "Como a cultura actual tenta minimizar ou negar a realidade do pecado? De que forma isso já influenciou o seu próprio pensar?",
                    "Em sua caminhada cristã, em que momentos você reconheceu, de modo particular, a profundidade da sua necessidade de graça?",
                    "Escreva uma oração de confissão e gratidão a Deus, reconhecendo a sua condição e a suficiência de Cristo.",
                ],
            ),
            ExerciciosBloco(
                titulo="III — Ministério e serviço",
                itens=[
                    "Você está a discipular alguém que pensa que «é bom suficiente» para ir ao céu. Como explicaria, com mansidão, a doutrina do pecado, usando as Escrituras?",
                    "Identifique uma situação concreta na sua igreja ou círculo onde o ensino sobre a perdição é negligenciado. Que passo dará para contribuir para um ensino mais fiel?",
                ],
            ),
        ],
        estudo_complementar={
            "titulo": "Efésios 2.1-10 — Mortos em delitos, vivificados em Cristo",
            "texto": "Leia com atenção Efésios 2.1-10. Paulo inicia descrevendo a condição anterior dos crentes e, a partir do versículo 4, introduz o «mas Deus, que é rico em misericórdia». Esta passagem é um dos resumos mais poderosos da condição humana e da iniciativa da graça.",
            "perguntas": [
                "Que palavras Paulo usa para descrever a condição prévia dos crentes (vv. 1-3)?",
                "Quem é o sujeito das acções nos versículos 4-6? O que isso nos diz sobre a iniciativa da salvação?",
                "Como se articulam, no versículo 8, a graça, a fé e o facto de que a salvação não vem de obras?",
                "Para que fomos criados em Cristo Jesus, segundo o versículo 10?",
            ],
        },
        proxima_apostila={
            "titulo": "A Graça de Deus em Cristo",
            "descricao": "Na próxima apostila — Apostila 2 — estudaremos a resposta de Deus ao estado de perdição humano: a sua graça revelada em Jesus Cristo. Veremos a natureza da graça, a sua iniciativa soberana e a obra de Cristo na cruz como único fundamento da salvação.",
            "preparar": [
                "Leia Romanos 3.21-26, Efésios 2.1-10 e Tito 2.11-14.",
                "Reflicta: em que difere a graça de um «prémio por bom comportamento»?",
                "Escreva uma lista de expressões populares sobre salvação que, em sua opinião, podem reduzir ou distorcer a graça bíblica.",
            ],
        },
        glossario=[
            GlossarioEntrada("Pecado", "Transgressão da lei de Deus e falha em corresponder à sua glória; estado de rebelião inerente à humanidade caída (Rm 3.23, 1 Jo 3.4)."),
            GlossarioEntrada("Queda", "Evento histórico registado em Génesis 3, no qual Adão e Eva desobedeceram a Deus, introduzindo o pecado e a morte em toda a criação."),
            GlossarioEntrada("Perdição", "Estado de separação de Deus em que se encontra todo ser humano fora de Cristo, com consequências presentes (morte espiritual) e eternas (morte eterna)."),
            GlossarioEntrada("Depravação total", "Doutrina bíblica que ensina que o pecado afectou todas as dimensões do ser humano (mente, vontade, coração, corpo), embora sem anular completamente a imagem de Deus."),
            GlossarioEntrada("Graça comum", "Benevolência geral de Deus que sustenta a criação, concede bênçãos a justos e injustos e refreia o pecado na sociedade, sem, no entanto, salvar."),
            GlossarioEntrada("Imagem de Deus (imago Dei)", "Qualidade constitutiva do ser humano criado por Deus, que inclui racionalidade, moralidade, relacionamento e domínio responsável, mesmo após a queda permanece, ainda que distorcida."),
        ],
        bibliografia=[
            "Bíblia Sagrada. Tradução de João Ferreira de Almeida, Revista e Corrigida.",
            "LLOYD-JONES, D. Martyn. Romanos: exposição. São Paulo: PES.",
            "MURRAY, John. A epístola aos Romanos. São Paulo: Cultura Cristã.",
            "EDWARDS, Jonathan. A história da redenção. São Paulo: Vida Nova.",
            "PACKER, J. I. Conhecendo a Deus. São Paulo: Cultura Cristã.",
            "STOTT, John R. W. A mensagem de Romanos. São Paulo: ABU.",
        ],
    )


def main():
    out_dir = REPO / "output" / "N01" / "I01" / "Fundamentos_da_Fe" / "Salvacao_e_Novo_Nascimento"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "EBE-APO-0001_O_Estado_de_Perdicao_do_Ser_Humano.docx"

    conteudo = build_demo()
    builder = DocumentBuilder(conteudo).build()
    builder.save(out_path)
    print(f"OK: {out_path}")


if __name__ == "__main__":
    main()
