import os
from random import randint

import jinja2


class Charts:
    def __init__(self):
        self._envrionment = jinja2.Environment()
        self._load_template()

    def _load_file(self, path):
        with open(path, "r") as f:
            content = f.read()
        return content

    def _load_template(self):
        path = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(path, "chart.html")
        self._template = self._load_file(template_path)

    def _generate_html(self, result):
        template = self._envrionment.from_string(self._template)
        html = template.render(**result)
        return html

    def _export_html(self, html, path="."):
        with open(path, "w") as f:
            f.write(html)

    def report(self, result, output_file):
        html = self._generate_html(result)
        self._export_html(html, output_file)

    def generate_chart(self, labels, datasets, title, yaxis, xaxis, output_path):
        result = {"labels": labels, "datasets": datasets, "title": title, "yaxis": yaxis, "xaxis": xaxis}
        self.report(result, output_path)

    def generate_dataset(self, legend, data, color="random"):
        if color == "random":
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)
            color = f"rgb({r}, {g}, {b})"
        dataset = {"legend": legend, "background_color": color, "border_color": color, "data": data}
        return dataset


if __name__ == "__main__":
    chart = Charts()
    labels = ["January", "February", "March", "April", "May", "June", "July"]
    legend1 = "My First dataset"
    color1 = "rgb(0, 255, 0)"
    data1 = [0, 10, 5, 2, 20, 30, 45]
    dataset1 = chart.generate_dataset(legend=legend1, data=data1)

    legend2 = "My second dataset"
    color2 = "rgb(0, 0, 255)"
    data2 = [0, 20, 5, 7, 20, 35, 45]
    dataset2 = chart.generate_dataset(legend=legend2, data=data2, color=color2)

    datasets = [dataset1, dataset2]
    yaxis = "Values"
    xaxis = "Month"
    title = "Trying draw a chart"
    path = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(path, "result.html")
    chart.generate_chart(
        labels=labels, datasets=datasets, title=title, yaxis=yaxis, xaxis=xaxis, output_path=output_path
    )
